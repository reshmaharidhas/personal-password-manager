import tkinter as tk
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
from datetime import datetime
import cryptocode
class sign_up_login:
    def __init__(self,server_username,server_password):
        self.root = tk.Tk()
        self.root.geometry("670x700")
        self.root.resizable(0,0)
        self.root.title("Personal Password Manager")
        self.root.config(bg="#ffc048")
        # images
        self.not_favorite_icon = tk.PhotoImage(file="assets/images/not_favorite_star.png").subsample(3,3)
        self.favorite_icon = tk.PhotoImage(file="assets/images/favorite_star.png").subsample(3,3)
        self.copy_icon = tk.PhotoImage(file="assets/images/copy-icon.png").subsample(2,2)
        self.key_icon = tk.PhotoImage(file="assets/images/icon_key.png").subsample(2,2)
        self.masterkey_icon = tk.PhotoImage(file="assets/images/master-key-48.png")
        self.icon_password = tk.PhotoImage(file="assets/images/icon_password_lock.png")
        self.add_icon = tk.PhotoImage(file="assets/images/add-icon.png").subsample(2,2)
        self.back_icon = tk.PhotoImage(file="assets/images/back_icon.png").subsample(2,2)
        # Database connection
        self.db = mysql.connector.connect(host="localhost",
                                          user=server_username,
                                          passwd=server_password)
        self.cursor_object = self.db.cursor()
        # Notebook
        self.myNotebook = ttk.Notebook(self.root)
        self.myNotebook.pack(expand=True)
        self.tab1Frame = tk.Frame(self.myNotebook, bg="#7ed6df",width=300)
        self.tab2Frame = tk.Frame(self.myNotebook, bg="blue",width=300)
        self.myNotebook.add(self.tab1Frame, text="Login")
        self.myNotebook.add(self.tab2Frame, text="Register")
        self.label1 = tk.Label(self.tab1Frame, text="Login with master password",bg="#7ed6df",fg="#000000",font=("Arial",14))
        self.label1.pack(padx=10,pady=30)
        self.entry_var = tk.StringVar()
        self.entry1 = tk.Entry(self.tab1Frame,textvariable=self.entry_var,font=("Arial",14),show="*")
        self.entry1.pack(padx=15)
        self.login_btn = tk.Button(self.tab1Frame,text="Login",command=self.login,font=("Arial",14),bg="black",fg="#ffffff",activebackground="#000000",activeforeground="#ffffff")
        self.login_btn.pack(padx=15,pady=10)
        self.label2 = tk.Label(self.tab2Frame, text="Register with new master password\n All data already saved will be deleted\n on registering with new master password",bg="blue",fg="#ffffff")
        self.label2.pack(pady=15)
        self.master_key_var = tk.StringVar()
        tk.Label(self.tab2Frame,text="Enter your new master password",font=("Georgia",14,"italic"),bg="blue",fg="white").pack()
        self.master_key_entry = tk.Entry(self.tab2Frame, textvariable=self.master_key_var,font=("Arial",14),show="*")
        self.master_key_entry.pack(padx=20,pady=14)
        self.register_btn = tk.Button(self.tab2Frame,bg="#000000",fg="#ffffff",text="Register",command=self.register_as_new_user,font=("Arial",14))
        self.register_btn.pack(pady=10)
        # Main UI
        self.container = tk.Frame(self.root,background="#ffc048")
        self.sidepanel = tk.Frame(self.container,background="#ffc048")
        self.sidepanel.pack(padx=30,side=tk.LEFT)
        self.app_btn = tk.Button(self.sidepanel,text="All",bg="#12CBC4",activebackground="#12CBC4",command=self.display_all_app_logins,font=("Arial",12),width=10)
        self.app_btn.grid(row=0,column=0,pady=7)
        self.favorites_btn = tk.Button(self.sidepanel,text="Favorites",bg="#12CBC4",activebackground="#12CBC4",command=self.display_favorited_logins,image=self.favorite_icon,compound=tk.LEFT,width=100,font=("Arial",10))
        self.favorites_btn.grid(row=1,column=0)
        # Frame
        self.buttons_frame_main = tk.Frame(self.container, background="#ffc048")
        self.buttons_frame_main.pack(pady=15)
        self.add_btn = tk.Button(self.buttons_frame_main,text="Add new",command=self.add_new_info,bg="blue",fg="#ffffff",font=("Times New Roman",16),image=self.add_icon,compound=tk.LEFT,padx=7)
        self.add_btn.grid(row=0,column=0)
        self.change_masterpassword_btn = tk.Button(self.buttons_frame_main,bg="#12CBC4",image=self.masterkey_icon,command=self.open_change_master_password_layout,text="Change Master password",compound=tk.LEFT,font=("Times New Roman",14),padx=7)
        self.change_masterpassword_btn.grid(row=0,column=2,padx=15,pady=5)
        # Frame
        self.main_panel = tk.Frame(self.container,background="#ffc048")
        self.main_panel.pack(pady=10)
        # Creating canvas
        self.canvas = tk.Canvas(self.main_panel, width=410, height=500)
        self.canvas.configure(bg="#ffffff")
        # Creating scrollbar
        self.scrollbar = tk.Scrollbar(self.main_panel, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, background="#70a1ff")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        # Setting app icon to display in the title bar.
        self.root.iconphoto(True,self.icon_password)
        self.root.mainloop()

    # Function to register as new user, or when user forgets their previously register master password.
    def register_as_new_user(self):
        self.create_database_tables()

    # Function to create new database and 2 new tables because user is registering newly.
    # This function is executed even when user forgets their registered master password.
    # All the content previously stored in the tables gets deleted when registering as new user again.
    def create_database_tables(self):
        if len(self.master_key_var.get())<=6:
            messagebox.showwarning("Invalid master key","Master key cannot be empty.\nPlease enter masker key of more than 6 alphanumeric characters")
        elif len(self.master_key_var.get())>6:
            # Check whether database is present or not.
            query = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'personal_pm_db';"
            self.cursor_object.execute(query)
            self.answer = self.cursor_object.fetchone()
            if self.answer:
                db_delete_query = "DROP DATABASE personal_pm_db;"
                self.cursor_object.execute(db_delete_query)
            # Create a database named 'personal_pm_db' if no such database exists.
            command_db_creation = "CREATE DATABASE personal_pm_db;"
            self.cursor_object.execute(command_db_creation)
            command_str = "USE personal_pm_db"
            self.cursor_object.execute(command_str)
            self.database_name_var = "personal_pm_db"
            # Check if there is table 'master_key_table' present in database 'personal_pm_db'.
            # If there is no such table, create table.
            try:
                query = "SELECT id FROM master_key_table;"
                self.cursor_object.execute(query)
                table_rows = self.cursor_object.fetchall()
            except Exception as err:
                query = "CREATE TABLE master_key_table (id VARCHAR(1),master_key VARCHAR(255) NOT NULL);"
                self.cursor_object.execute(query)
                # Insert master key into the table 'master_key_table'.
                insert_master_key_query = "INSERT INTO master_key_table (id,master_key) VALUES (%s,%s)"
                self.cursor_object.execute(insert_master_key_query,("1",self.master_key_var.get()))
                self.db.commit()
                query = "CREATE TABLE app_table (id int NOT NULL AUTO_INCREMENT,app_name VARCHAR(255) NOT NULL,userid VARCHAR(255),app_password VARCHAR(255) NOT NULL,app_url VARCHAR(255),date_creation VARCHAR(20),date_modified VARCHAR(20),favorite TINYINT(1),PRIMARY KEY (id));"
                self.cursor_object.execute(query)
                messagebox.showinfo("Registered","All previous stored data is deleted.\nNew master password saved.")
                self.myNotebook.destroy()
                # Show the main UI with scrolling canvas.
                self.container.pack(pady=20)
                display_query = "SELECT * FROM app_table;"
                self.display_refreshed_data(display_query)

    # Function to login the server with the master password already registered.
    def login(self):
        self.cursor_object.execute("USE personal_pm_db")
        user_entered_master_key = self.entry_var
        query = "SELECT * FROM master_key_table WHERE id='1';"
        self.cursor_object.execute(query)
        result = self.cursor_object.fetchone()
        if result[1]==self.entry_var.get():
            self.myNotebook.destroy()
            self.container.pack(pady=20)
            display_query = "SELECT * FROM app_table;"
            self.display_refreshed_data(display_query)
        else:  # Warns user when the user entered master password is wrong. Does not login.
            messagebox.showwarning("Wrong","Wrong master password!")

    # Function to display rows from table 'app_table' based on the given query 'query_to_run'.
    def display_refreshed_data(self,query_to_run):
        try:
            self.cursor_object.execute(query_to_run)
            # Delete all widgets inside the frame 'scrollable_frame'.
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            # Add new widgets to frame 'scrollable_frame' byb fetching data from the table.
            result = self.cursor_object.fetchall()
            for record_ptr in range(len(result)):
                user_data = result[record_ptr][1]
                # Create a frame to place the Label and Button widgets in it.
                inner_frame = tk.Frame(self.scrollable_frame)
                inner_frame.grid(row=record_ptr,column=0,pady=2)
                person_var = tk.IntVar()
                person_var.set(result[record_ptr][0])
                # Label widget containing user data from fetched from table
                appwebsitename_label = tk.Label(inner_frame, bg="white",fg="#000000", font=("Times New Roman", 14), width=420, padx=2,text=user_data,anchor=tk.W,image=self.key_icon,compound=tk.LEFT)
                appwebsitename_label.pack(anchor=tk.W)
                account_userid_label = tk.Label(inner_frame,font=("Times New Roman", 9),text=result[record_ptr][2],width=60,anchor=tk.W,bg="#ffffff",fg="blue")
                account_userid_label.pack(anchor=tk.W)
                appwebsitename_label.bind("<Button-1>",lambda event,details=result[record_ptr][0]:self.open_information(details))
        except:
            messagebox.showerror("Error occurred", "Unable to refresh")

    # Function to show user interface to insert new password data to the table 'app_table'.
    def add_new_info(self):
        # Hide
        self.buttons_frame_main.pack_forget()
        self.sidepanel.pack_forget()
        self.main_panel.pack_forget()
        # Create a new frame
        self.add_container = tk.Frame(self.container,background="#ffc048")
        self.add_container.pack(padx=14)
        # Back button
        self.back_btn = tk.Button(self.add_container,text="Back",fg="#ffffff",bg="#000000",command=lambda :self.back_button_clicked(self.add_container),font=("Arial",14),image=self.back_icon,compound=tk.LEFT,activebackground="#000000",activeforeground="#ffffff")
        self.back_btn.grid(row=0,column=0,pady=10)
        tk.Label(self.add_container,text="App/Website:",font=("Arial",14),bg="#ffc048").grid(row=1,column=0,pady=5)
        self.app_website_name_var = tk.StringVar()
        self.app_website_name_entry=tk.Entry(self.add_container,textvariable=self.app_website_name_var,font=("Arial",14))
        self.app_website_name_entry.grid(row=1,column=1,pady=5)
        tk.Label(self.add_container,text="User id:",font=("Arial",14),bg="#ffc048").grid(row=2,column=0,pady=5)
        self.app_website_userid_var = tk.StringVar()
        self.app_website_userid_entry = tk.Entry(self.add_container,textvariable=self.app_website_userid_var,font=("Arial",14))
        self.app_website_userid_entry.grid(row=2,column=1,pady=5)
        tk.Label(self.add_container,text="Password:",font=("Arial",14),bg="#ffc048").grid(row=3,column=0,pady=5)
        self.app_website_password_var = tk.StringVar()
        self.app_website_password_entry = tk.Entry(self.add_container,textvariable=self.app_website_password_var,font=("Arial",14),show="*")
        self.app_website_password_entry.grid(row=3,column=1,pady=5)
        tk.Label(self.add_container,text="URL:",font=("Arial",14),bg="#ffc048").grid(row=4,column=0)
        self.app_website_url_var = tk.StringVar()
        self.app_website_url_entry = tk.Entry(self.add_container, textvariable=self.app_website_url_var,font=("Arial",14))
        self.app_website_url_entry.grid(row=4, column=1,pady=5)
        add_data_btn = tk.Button(self.add_container,text="Save",bg="blue",fg="#ffffff",font=("Arial",14),command=lambda :self.insert_data_to_app_table(self.app_website_name_var.get(),self.app_website_userid_var.get(),self.app_website_password_var.get(),self.app_website_url_var.get()))
        add_data_btn.grid(row=5,column=0,pady=7)

    # Function to insert new password data to the table 'app_table'.
    def insert_data_to_app_table(self,appwebsitename_input,appwebsite_userid_input,appwebsite_password_input,appwebsite_url_input):
        if appwebsitename_input!="" and appwebsite_password_input!="":
            query = "SELECT COUNT(*) FROM app_table WHERE app_name=%s and userid=%s"
            self.cursor_object.execute(query,(appwebsitename_input,appwebsite_userid_input))
            ans = self.cursor_object.fetchone()
            if ans[0]==0:
                current_time = str(datetime.now())[:19]
                masterkey_query = "SELECT * FROM master_key_table WHERE id=1"
                self.cursor_object.execute(masterkey_query)
                extracted_master_key = self.cursor_object.fetchone()
                appwebsite_password_input = self.encrypt_password(extracted_master_key[1],appwebsite_password_input)
                query = "INSERT INTO app_table (app_name,userid,app_password,app_url,date_creation,favorite) VALUES (%s,%s,%s,%s,%s,False);"
                self.cursor_object.execute(query,(appwebsitename_input,appwebsite_userid_input,appwebsite_password_input,appwebsite_url_input,current_time))
                self.db.commit()
                self.back_button_clicked(self.add_container)
            else:
                messagebox.showwarning("Data already present","Same website's information for same user id is stored already!\nAdd with different user id of that account")
        else:
            messagebox.showwarning("Invalid","App/website name and password cannot be empty!")

    # Function to return back to the home screen of the password manager app by deleting the given 'current_frame' passed as argument.
    def back_button_clicked(self,current_frame):
        current_frame.destroy()
        self.buttons_frame_main.pack()
        self.sidepanel.pack(side=tk.LEFT,padx=30)
        self.main_panel.pack()
        display_query = "SELECT * FROM app_table;"
        self.display_refreshed_data(display_query)


    # Function to display the currently selected account details in a layout.
    def open_information(self,id_selected):
        # Hide
        self.buttons_frame_main.pack_forget()
        self.sidepanel.pack_forget()
        self.main_panel.pack_forget()
        # Create a frame to display the details.
        self.display_container = tk.Frame(self.container,width=300,background="#ffc048")
        self.display_container.pack()
        query = "SELECT * FROM app_table WHERE id=%s"
        self.cursor_object.execute(query,(id_selected,))
        details_arr = self.cursor_object.fetchone()
        display_buttons_frame = tk.Frame(self.display_container,background="#ffc048")
        display_buttons_frame.grid(row=0,column=0,columnspan=2,pady=15)
        self.back_btn = tk.Button(display_buttons_frame,text="Back",fg="white",bg="black",command=lambda :self.back_button_clicked(self.display_container),font=("Arial",14),image=self.back_icon,compound=tk.LEFT,padx=7)
        self.back_btn.grid(row=0,column=0,padx=15)
        set_favorite_btn = tk.Button(display_buttons_frame,command=lambda :self.change_favorite_status(details_arr[0],set_favorite_btn),bg="#ffffff")
        set_favorite_btn.grid(row=0,column=1,padx=10)
        self.edit_btn = tk.Button(display_buttons_frame,text="Edit",fg="white",bg="purple",font=("Arial",14))
        self.edit_btn.grid(row=0,column=2,padx=10)
        delete_btn = tk.Button(display_buttons_frame,text="Delete",fg="white",bg="red",command=lambda:self.delete_data(details_arr[0],self.display_container),font=("Arial",14))
        delete_btn.grid(row=0,column=3,padx=6)
        self.savechanges_btn = tk.Button(display_buttons_frame, text="Save changes", fg="white", bg="blue",font=("Arial",14))
        # Data retrieved
        tk.Label(self.display_container,text="App/Website name:",font=("Arial",14),bg="#ffc048").grid(row=1,column=0)
        data1 = tk.Label(self.display_container,text=details_arr[1],font=("Arial",14),bg="#ffc048")
        data1.grid(row=1,column=1)
        tk.Label(self.display_container,text="Login id:",font=("Arial",14),bg="#ffc048").grid(row=2,column=0)
        data2 = tk.Label(self.display_container,text=details_arr[2],font=("Arial",14),bg="#ffc048")
        data2.grid(row=2,column=1)
        new_userid = tk.StringVar()
        entry_widget2 = tk.Entry(self.display_container,textvariable=new_userid)
        tk.Label(self.display_container,text="Password:",font=("Arial",14),bg="#ffc048").grid(row=3,column=0)
        self.cursor_object.execute("SELECT * FROM master_key_table WHERE id=1")
        extracted_master_key = self.cursor_object.fetchone()
        decrypted_passwrd = self.get_decrypted_password(extracted_master_key[1],details_arr[3])
        data3 = tk.Label(self.display_container,text=decrypted_passwrd,font=("Arial",14),bg="#ffc048")
        data3.grid(row=3,column=1)
        copy_btn = tk.Button(self.display_container,command=lambda :self.copy_password(decrypted_passwrd),image=self.copy_icon)
        copy_btn.grid(row=3,column=2)
        new_password = tk.StringVar()
        entry_widget3 = tk.Entry(self.display_container,textvariable=new_password)
        tk.Label(self.display_container,text="URL:",font=("Arial",14),bg="#ffc048").grid(row=4,column=0)
        data4 = tk.Label(self.display_container,text=details_arr[4],fg="blue",font=("Arial",14),bg="#ffc048")
        data4.grid(row=4,column=1)
        new_url = tk.StringVar()
        entry_widget4 = tk.Entry(self.display_container, textvariable=new_url)
        # Display the date of creation of this login account.
        tk.Label(self.display_container,text="Date created:",font=("Arial",14),bg="#ffc048").grid(row=5,column=0)
        tk.Label(self.display_container,text=details_arr[5],font=("Arial",14),bg="#ffc048").grid(row=5,column=1)
        # Display the date when the details are modified recently.
        tk.Label(self.display_container, text="Date modified:",font=("Arial",14),bg="#ffc048").grid(row=6, column=0)
        tk.Label(self.display_container, text=details_arr[6],font=("Arial",14),bg="#ffc048").grid(row=6, column=1)
        if details_arr[7]==1:
            set_favorite_btn.config(image=self.favorite_icon)
        elif details_arr[7]==0:
            set_favorite_btn.config(image=self.not_favorite_icon)
        self.edit_btn.config(command=lambda :self.edit_current_information(self.display_container,copy_btn,details_arr,data2,data3,data4,entry_widget2,new_userid,entry_widget3,new_password,entry_widget4,new_url,self.edit_btn,self.savechanges_btn))
    def edit_current_information(self,framename,copy_btn,details_arr,data2,data3,data4,widget2,widget2_var,widget3,widget3_var,widget4,widget4_var,edit_btn,savechanges_btn):
        # Hide
        data2.grid_forget()
        data3.grid_forget()
        data4.grid_forget()
        edit_btn.destroy()
        copy_btn.grid_forget()
        # Show the button 'Save Changes'
        savechanges_btn.grid(row=0,column=2)
        widget2.grid(row=2,column=1)
        widget2.insert(0,details_arr[2])
        # Decrypt encrypted password
        self.cursor_object.execute("SELECT * FROM master_key_table WHERE id=1")
        extracted_master_key = self.cursor_object.fetchone()
        decrypted_passwrd = self.get_decrypted_password(extracted_master_key[1], details_arr[3])
        widget3.grid(row=3,column=1)
        widget3.insert(0,decrypted_passwrd)
        widget4.grid(row=4, column=1)
        widget4.insert(0, details_arr[4])
        savechanges_btn.config(command=lambda :self.update_data_app_table(details_arr[0],details_arr[1],widget2_var.get(),widget3_var.get(),widget4_var.get(),savechanges_btn))

    # Function to update changes to the specific row in the table 'app_table'.
    def update_data_app_table(self,id_num,appwebsitename,widget2_var,widget3_var,widget4_var,savechanges_btn):
        query = "SELECT COUNT(*) FROM app_table WHERE app_name=%s and userid=%s"
        self.cursor_object.execute(query,(appwebsitename,widget2_var))
        ans = self.cursor_object.fetchone()
        other_account_id = 0
        if ans[0]==1:
            self.cursor_object.execute("SELECT id FROM app_table WHERE app_name=%s and userid=%s;",(appwebsitename,widget2_var))
            other_account_id=self.cursor_object.fetchone()[0]
        if ans[0]==0 or (ans[0]==1 and other_account_id==id_num):
            current_time = str(datetime.now())[0:19]
            # Encrypt the newly entered password and update it to database.
            self.cursor_object.execute("SELECT * FROM master_key_table WHERE id=1")
            extracted_master_key = self.cursor_object.fetchone()
            widget3_var = self.encrypt_password(extracted_master_key[1],widget3_var)
            formula = f"UPDATE app_table SET userid=%s,app_password=%s,app_url=%s,date_modified=%s WHERE id={id_num};"
            self.cursor_object.execute(formula,(widget2_var,widget3_var,widget4_var,current_time))
            self.db.commit()
            self.savechanges_btn.destroy()
            messagebox.showinfo("Updated","Changes saved")
        else:
            messagebox.showerror("Duplicate data found","Account with same user id already available\nCould not update!")


    # Function to delete a detail stored in the password manager.
    def delete_data(self,id_to_delete,frame_to_delete):
        # Prompts user to confirm the deletion process.
        # If user clicks 'Yes', it gets deleted. Otherwise, it is not deleted.
        if messagebox.askyesnocancel("Delete?","Do you really want to delete this from your password manager?")==True:
            query = f"DELETE FROM app_table WHERE id={id_to_delete};"
            self.cursor_object.execute(query)
            self.db.commit()
            self.back_button_clicked(frame_to_delete)
            messagebox.showinfo("Deleted","Deleted successfully!")


    # Function to encode and encrypt a given word 'password_input' with a key 'masterkey_extracted'.
    # The encrypted content can be decoded only with the help of the key 'masterkey_extracted'.
    def encrypt_password(self,masterkey_extracted,password_input):
        secure_key = masterkey_extracted + "1900aZAz" # Adding some more characters before storing in the table 'app_table'.
        encoded_data = cryptocode.encrypt(password_input, secure_key)
        return encoded_data

    # Function to decode and decrypt a given word 'encrypted_password' with a key 'masterkey_extracted'.
    # The encrypted content can be decoded only with the help of the key 'masterkey_extracted'.
    def get_decrypted_password(self,masterkey_extracted,encrypted_password):
        secure_key = masterkey_extracted + "1900aZAz"
        decoded_data = cryptocode.decrypt(encrypted_password,secure_key)
        return decoded_data

    # Function to make an account details as favorite or not by clicking a button 'favourite_button'.
    # This updates the value in the table 'app_table' as 1 when it is starred. And changes to 0, when it is removed from favorites.
    def change_favorite_status(self,id_selected,favourite_button):
        self.cursor_object.execute(f"SELECT favorite FROM app_table WHERE id={id_selected};")
        favourite_status = self.cursor_object.fetchone()[0]
        changed_status = None
        if favourite_status==0:
            changed_status = True
        else:
            changed_status = False
        formula = f"UPDATE app_table SET favorite={changed_status} WHERE id={id_selected};"
        self.cursor_object.execute(formula)
        self.db.commit()
        # Change the image in the button to yellow star if 'changed_status' is True.
        if changed_status is True:
            favourite_button.config(image=self.favorite_icon)
        else:
            favourite_button.config(image=self.not_favorite_icon)

    # Function to copy the content 'password_stored' to the clipboard.
    def copy_password(self,password_stored):
        self.root.clipboard_clear()
        self.root.clipboard_append(password_stored)


    # Function to display all rows which are both favorites and not favorites.
    def display_all_app_logins(self):
        display_query = "SELECT * FROM app_table;"
        self.display_refreshed_data(display_query)

    # Function to display all rows which are marked as favorites.
    # This displays the rows which have the column 'favorite' as 1.
    def display_favorited_logins(self):
        display_query = "SELECT * FROM app_table WHERE favorite=1;"
        self.display_refreshed_data(display_query)

    # Function to open the user interface for changing the master password.
    def open_change_master_password_layout(self):
        self.buttons_frame_main.pack_forget()
        self.sidepanel.pack_forget()
        self.main_panel.pack_forget()
        self.display_container = tk.Frame(self.container,background="#ffc048")
        self.display_container.pack()
        tk.Label(self.display_container,text="Change your master password",font=("Arial",22),bg="#ffc048").pack(pady=10)
        tk.Button(self.display_container,text="Back",font=("Arial",12),command=lambda :self.back_button_clicked(self.display_container),bg="black",fg="white",image=self.back_icon,compound=tk.LEFT,padx=7).pack(anchor=tk.W)
        tk.Label(self.display_container,text="Old master password",font=("Arial",12),bg="#ffc048").pack(pady=4)
        old_master_password_var = tk.StringVar()
        entry_old_master_password_widget = tk.Entry(self.display_container,show="*",textvariable=old_master_password_var,font=("Arial",12))
        entry_old_master_password_widget.pack(pady=4)
        tk.Label(self.display_container,text="Confirm old master password",font=("Arial",12),bg="#ffc048").pack(pady=4)
        confirm_old_master_password_var = tk.StringVar()
        entry_confirm_old_master_password_widget = tk.Entry(self.display_container,show="*",textvariable=confirm_old_master_password_var,font=("Arial",12))
        entry_confirm_old_master_password_widget.pack(pady=4)
        tk.Label(self.display_container,text="New master password",font=("Arial",12),bg="#ffc048").pack(pady=4)
        new_master_password_var = tk.StringVar()
        entry_new_master_password_widget = tk.Entry(self.display_container,
                                                            textvariable=new_master_password_var,font=("Arial",12),show="*")
        entry_new_master_password_widget.pack(pady=4)
        tk.Button(self.display_container,text="Change",font=("Arial",12),bg="purple",fg="white",command=lambda :self.change_all_passwords(old_master_password_var.get(),confirm_old_master_password_var.get(),new_master_password_var.get(),self.display_container)).pack(pady=12)


    # Function to change all password values in table in encrypted form based on the newly changed master password.
    def change_all_passwords(self,old_master_password,confirmed_old_master_password,new_master_password,current_frame):
        query = "SELECT * FROM master_key_table WHERE id=1"
        self.cursor_object.execute(query)
        extracted_master_key = self.cursor_object.fetchone()
        # If the old password and the password typed in the confirmation field is not same, show warning.
        if old_master_password!=confirmed_old_master_password:
            messagebox.showwarning("Mismatch","Old passwords not matching with confirmed old password")
        elif len(new_master_password)<10:  # Master password is less than 10 length, warn the user.
            messagebox.showwarning("Invalid new master password","Master password length cannot be less than 10")
        elif extracted_master_key[1]==old_master_password and len(new_master_password)>=10:
            query = "SELECT * FROM app_table;"
            self.cursor_object.execute(query)
            result = self.cursor_object.fetchall()
            # Iterate through every row in the table 'app_table'.
            for record in result:
                # Get the decrypted password of current row.
                decrypted_passwrd = self.get_decrypted_password(extracted_master_key[1], record[3])
                # Encrypt the retrieved decrypted password with the new master password.
                widget3_var = self.encrypt_password(new_master_password, decrypted_passwrd)
                # Calculate the current date and time.
                current_time = str(datetime.now())[0:19]
                formula = f"UPDATE app_table SET app_password=%s,date_modified=%s WHERE id={record[0]};"
                # Run the query to update.
                self.cursor_object.execute(formula, (widget3_var,current_time))
                self.db.commit()
            # Update the new master password
            query = "UPDATE master_key_table SET master_key=%s WHERE id=1;"
            self.cursor_object.execute(query,(new_master_password,))
            self.db.commit()
            self.back_button_clicked(current_frame)
        else:
            messagebox.showwarning("Wrong old master password","Please enter your correct old master password!")
