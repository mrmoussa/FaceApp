import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5 import QtSql
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QMessageBox
from PyQt5.QtSql import QSqlDatabase


from camera import MainWindow

# First login class will be runned
class LoginScreen(QMainWindow):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        
        #Login button click activation
        self.login.clicked.connect(self.loginfunction)
        
    # login button logic function
    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        db = QSqlDatabase("QPSQL")
        db.setUserName("postgres")  
        db.setPassword("postgres")
        db.setDatabaseName("universitydb")


        if not db.open():
            print("Unable to connect.")
            print('Last error', db.lastError().text())
            sys.exit(1)
        
        query = QtSql.QSqlQuery(db)
        print("------")
        print(query.exec("SELECT * from instructor where inst_name = '" + user + "' AND inst_pwd = '" + password + "'"))
        print(query.size())
        if query.size() == 0:
            print("User not found.")
            loadUi("login.ui",self)
            self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        
        #Login button click activation
            self.login.clicked.connect(self.loginfunction)
        else:     
        # code which gets us to the next window where professor fills in form
            form = ProfessorForm()
            widget.addWidget(form)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        
class ProfessorForm(QMainWindow):
    def __init__(self):
        super(ProfessorForm, self).__init__()
        loadUi("profform.ui",self)

        self.enterbtn.clicked.connect(self.enterfunction)
   
    # camera window call function
    def enterfunction(self):
        secnofield = self.secnofield.text()
        fnamefield = self.fnamefield.text()
        lnamefield = self.lnamefield.text()
        datefield = self.datefield.text()
        subjectfield = self.subjectfield.text()

     
        print(secnofield)
        print(lnamefield)
        print(fnamefield)
        print(datefield)
        print(subjectfield)


        db = QSqlDatabase("QPSQL")
        db.setUserName("postgres")  
        db.setPassword("postgres")
        db.setDatabaseName("universitydb")


        if not db.open():
            print("Unable to connect.")
            print('Last error', db.lastError().text())
            sys.exit(1)
        
        query = QtSql.QSqlQuery(db)
        query.exec("INSERT INTO record VALUES ('" +fnamefield +"', '" +lnamefield+ "', '"+ subjectfield+"', '"+ secnofield +"', '"+ datefield  +"');")
    
        entercamera = MainWindow()
        widget.addWidget(entercamera)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# main function. First login page is called
app = QApplication(sys.argv)
login = LoginScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(login)
widget.setFixedHeight(650)
widget.setFixedWidth(800)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")