from PyQt5 import QtGui, QtSql
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QMessageBox
import sys
from PyQt5.QtSql import QSqlDatabase

def create_connection(database):
    db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(database)
    if not db.open():
        print("Cannot open database")
        print(
            "Unable to establish a database connection.\n"
            "This example needs SQLite support. Please read "
            "the Qt SQL driver documentation for information "
            "how to build it.\n\n"
            "Click Cancel to exit."
        )
        return False

    query = QtSql.QSqlQuery()
    if not query.exec_(
        """CREATE TABLE IF NOT EXISTS Groups (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "group_name" TEXT)"""
    ):
        print(query.lastError().text())
        return False
    if not query.exec_(
        """CREATE TABLE IF NOT EXISTS Student (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "group_id" INTEGER,
    "name" TEXT,
    "age" INTEGER,
    FOREIGN KEY(group_id) REFERENCES Groups(id))"""
    ):
        print(query.lastError().text())
        return False
    return True


class AddGroupDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title_le = QtWidgets.QLineEdit()

        button_box = QtWidgets.QDialogButtonBox(self)
        button_box.setOrientation(QtCore.Qt.Horizontal)
        button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.title_le)
        lay.addWidget(button_box)

    @property
    def title(self):
        return self.title_le.text()


class EditMacroDialog(QtWidgets.QDialog):
    def __init__(self, model, index, parent=None):
        super().__init__(parent)

        self._group_id = model.record(index).value("id")

        self.title_le = QtWidgets.QLineEdit()

        self.student_table_model = QtSql.QSqlTableModel()
        self.student_table_model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.student_table_model.setTable("Student")
        self.student_table_model.setFilter("group_id={}".format(self.group_id))
        self.student_table_model.select()
        self.table_view = QtWidgets.QTableView(selectionBehavior=QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setModel(self.student_table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        for name in ("group_id", "id"):
            self.table_view.hideColumn(self.student_table_model.record().indexOf(name))
        self.table_view.verticalHeader().hide()

        self.plus_button = QtWidgets.QPushButton(self.tr("+"))
        self.minus_button = QtWidgets.QPushButton(self.tr("-"))
        self.save_button = QtWidgets.QPushButton(self.tr("Save"))

        mapper = QtWidgets.QDataWidgetMapper(
            self, submitPolicy=QtWidgets.QDataWidgetMapper.ManualSubmit
        )
        mapper.setModel(model)
        mapper.addMapping(self.title_le, model.record().indexOf("group_name"))
        mapper.setCurrentIndex(index)

        self.plus_button.clicked.connect(self.addRow)
        self.minus_button.clicked.connect(self.removeRow)

        self.save_button.clicked.connect(mapper.submit)
        self.save_button.clicked.connect(self.accept)

        hlay = QtWidgets.QHBoxLayout(self)

        vlay = QtWidgets.QVBoxLayout()
        vlay.addWidget(self.title_le)
        vlay.addWidget(self.table_view)
        hlay.addLayout(vlay)

        vlay2 = QtWidgets.QVBoxLayout()
        vlay2.addWidget(self.plus_button)
        vlay2.addWidget(self.minus_button)
        vlay2.addWidget(self.save_button)
        hlay.addLayout(vlay2)

    @property
    def group_id(self):
        return self._group_id

    @QtCore.pyqtSlot()
    def addRow(self):
        r = self.student_table_model.record()
        r.setValue("group_id", self.group_id)
        if self.student_table_model.insertRecord(
            self.student_table_model.rowCount(), r
        ):
            self.student_table_model.select()

    @QtCore.pyqtSlot()
    def removeRow(self):
        ixs = self.table_view.selectionModel().selectedIndexes()
        if ixs:
            self.student_table_model.removeRow(ixs[0].row())
            self.student_table_model.select()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._model = QtSql.QSqlTableModel(self)
        self.model.setTable("Groups")
        self.model.select()

        self.sql_list_view = QtWidgets.QListView()
        self.sql_list_view.setModel(self.model)
        self.sql_list_view.setModelColumn(self.model.record().indexOf("group_name"))

        self.new_button = QtWidgets.QPushButton(self.tr("New"))
        self.edit_button = QtWidgets.QPushButton(self.tr("Edit"))
        self.remove_button = QtWidgets.QPushButton(self.tr("Remove"))

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        grid_layout = QtWidgets.QGridLayout(central_widget)
        grid_layout.addWidget(
            QtWidgets.QLabel(self.tr("Groups"), alignment=QtCore.Qt.AlignCenter)
        )
        grid_layout.addWidget(self.sql_list_view, 1, 0)

        vlay = QtWidgets.QVBoxLayout()
        vlay.addWidget(self.new_button)
        vlay.addWidget(self.edit_button)
        vlay.addWidget(self.remove_button)
        grid_layout.addLayout(vlay, 1, 1)
        self.resize(640, 480)

        self.new_button.clicked.connect(self.new)
        self.edit_button.clicked.connect(self.edit)
        self.remove_button.clicked.connect(self.remove)

        self.sql_list_view.selectionModel().selectionChanged.connect(
            self.onSelectionChanged
        )
        self.onSelectionChanged()

    @property
    def model(self):
        return self._model

    @QtCore.pyqtSlot()
    def new(self):
        d = AddGroupDialog()
        if d.exec_() == QtWidgets.QDialog.Accepted:
            r = self.model.record()
            r.setValue("group_name", d.title)
            if self.model.insertRecord(self.model.rowCount(), r):
                self.model.select()

    @QtCore.pyqtSlot()
    def edit(self):
        ixs = self.sql_list_view.selectionModel().selectedIndexes()
        if ixs:
            d = EditMacroDialog(self.model, ixs[0].row())
            d.exec_()

    @QtCore.pyqtSlot()
    def remove(self):
        ixs = self.sql_list_view.selectionModel().selectedIndexes()
        if ixs:
            row = ixs[0].row()
            id_ = self.model.record(row).value("id")
            query = QtSql.QSqlQuery()
            query.prepare("DELETE FROM Student WHERE group_id = ?")
            query.addBindValue(id_)
            if not query.exec_():
                print(query.lastError().text())
                return
            self.model.removeRow(row)
            self.model.select()

    @QtCore.pyqtSlot()
    def onSelectionChanged(self):
        state = bool(self.sql_list_view.selectionModel().selectedIndexes())
        self.edit_button.setEnabled(state)
        self.remove_button.setEnabled(state)


if __name__ == "__main__":
    import sys

    database = "database.db"  # ":memory:"
    app = QtWidgets.QApplication(sys.argv)
    if not create_connection(database):
        sys.exit(app.exec_())
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())