import sql_connection as sql 
import json, os, psycopg2
from tkinter import ttk, messagebox
from tkinter import *


bottom_color = "#edbf87"



def error_function( error ):
    messagebox.showinfo( message = "Something went wrong: \n" + str( error ) , title="Query error")


def main_view_connection():
    
    def connectDatabase ():

        host          = server.get()
        database_con  = database.get()
        user_con      = user.get()
        password_con  = password.get()
        port_con      = port.get()


        # host         = "leoviquez.com"
        # database_con = "basesII"
        # user_con     = "basesII"
        # port_con     = "5432"
        # password_con = "12345"


        connection = sql.Connection( database_con, host, user_con, password_con, port_con  )
        pool = connection.connect_to_database( )

        if ( pool ):
            #cursor = pool.cursor()
            ventana.destroy()
            privilege_view( connection )

    ventana = Tk()
    ventana.geometry("580x350+400+100")
    ventana.title(" Sql Server Connection")
    ventana['background'] = bottom_color

    e3 = Label(ventana, text="Connection Login", bg = bottom_color)
    e3.pack(padx=5, pady=5, ipadx=2, ipady=2)
    e3.place(x = 230, y = 20)

    Label(ventana,  text = "Servidor", bg = bottom_color).place(x = 80, y = 80) 

    Label(ventana,  text = "Base", bg = bottom_color).place(x = 80, y = 120)   

    Label(ventana,  text = "Puerto", bg = bottom_color).place(x= 80, y = 160)

    Label(ventana,  text = "Usuario", bg = bottom_color).place(x = 80, y = 200)  

    Label(ventana,  text = "Contraseña", bg = bottom_color).place(x = 80, y = 240)


    server = Entry(ventana, width = 30)  
    server.place(x = 200, y = 80)  

    database = Entry(ventana, width = 30)
    database.place(x = 200, y = 120) 

    port = Entry(ventana, width = 30)
    port.place(x= 200, y = 160)

    user = Entry(ventana, width = 30)
    user.place(x = 200, y = 200) 

    password = Entry(ventana, show="*", width = 30)
    password.place(x = 200, y = 240) 

    submit_button = Button(ventana,  text = "Connect", width = 25, height = 1, command = connectDatabase)
    submit_button.place(x = 200, y = 280) 


    ventana.mainloop()






def privilege_view( connection ):

    def tables_insert( ):

        pool    = connection.connect_to_database()
        cursor  = pool.cursor()

        try:
            cursor.execute( "SELECT tablename from pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema' " )
            row = cursor.fetchall()

            tables_list = []

            if ( len ( row ) != 1 ):
                
                for table_name in  row:
                    tables_list.append( table_name[0] )
            
            else:
                tables_list.append( row[0][0] )

            combo_tables["values"] = tables_list
            cursor.close()

        except Exception as error:

            error_function( error )
            cursor.close()
    
    
    def fill_schema_selector( row ):
        schemas = [] 

        if ( len( row  ) != 1 ):
            for schema_name in row:
                schemas.append( schema_name[0] )
        else:
            schemas.append( row[0][0] )

        combo_schema["values"] = schemas

        
    def fill_selector( evt ):

        if ( len( combo_tables.get() ) != 0 ):

            pool    = connection.connect_to_database()
            cursor  = pool.cursor()

            try:                
                combo_colum["values"] = []   
                cursor.execute("SELECT COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" + combo_tables.get() + "'")  
                column_names = cursor.fetchall()
                columns_values = []
        
                for column_name in column_names:
                    columns_values.append( column_name[0] )

                combo_colum["values"] = columns_values

                query = "SELECT schema_name FROM INFORMATION_SCHEMA.SCHEMATA as sche " \
                        "INNER JOIN INFORMATION_SCHEMA.TABLES as sta ON sche.schema_name = sta.table_schema " \
                        "WHERE STA.table_name = '{}'".format( combo_tables.get() ) 

                cursor.execute( query )               
                row = cursor.fetchall()
                cursor.close()
                fill_schema_selector( row )
                
            except Exception as error:
                error_function ( error )
                cursor.close()
            
    def get_privileges():

        pool    = connection.connect_to_database()
        cursor  = pool.cursor()

        if ( combo_colum.get() and confirmation_var.get() and combo_tables.get() and combo_schema.get() ):
            
            try:
                query = "SELECT * FROM INFORMATION_SCHEMA.column_privileges where table_name = '{}' "\
                        "and column_name = '{}' and table_schema = '{}'".format(    combo_tables.get(), 
                                                                                    combo_colum.get(), 
                                                                                    combo_schema.get() 
                                                                                )
                print ( query )
                cursor.execute( query )
                row = cursor.fetchall()
                fill_text_box( row, 0  )

            except Exception as error:
                error_function( error )


        elif ( combo_tables.get() and combo_schema.get() ):
            
            try:

                query = "SELECT * FROM INFORMATION_SCHEMA.table_privileges where table_name = '{}' " \
                        "and table_schema = '{}'".format( combo_tables.get(), combo_schema.get() )
                
                print ( query )
                cursor.execute( query )
                row = cursor.fetchall()
                cursor.close()
                fill_text_box( row, 1 )
            
            except Exception as error:
                error_function ( error )
                cursor.close()
        

    def fill_text_box( response, type_get ):

        text_result = ""

        if ( type_get == 1 ):

            text_result +=  "Nombre de la tabla:  " + response[0][4].lower() + "\n" \
                            "Usuario consultado: "  + connection.user + "\n" \
                            "Esquema consultado: "  + combo_schema.get() + "\n\n"
                       
            
            for privilege_name in response:
                text_result += "Privelegio: {} \n".format( privilege_name[5] )
     
        else:

            text_result  += "Nombre de la tabla: " + response[0][2].lower() + "\n" \
                            "Columna consultada: " + response[0][5] + "\n" \
                            "Usuario consultado: " + connection.user +"\n" \
                            "Esquema consultado: " + combo_schema.get() + "\n\n"

            for column_name in response:
                text_result += "Privelegio: {} \n".format( column_name[6] )        
        
        response_text = Text( ventana )
        response_text.config( width=35, height=10, font=("Arial",10), padx=50, pady=15 )
        response_text.place( x = 240, y = 60)
        response_text.insert( END,text_result )

    
    def back():
        ventana.destroy()
        main_view_connection()

    def endView():
        ventana.destroy()
        plan_execution_view( connection )

    ventana = Tk()
    ventana.geometry("760x470+340+100")
    ventana.title(" Sql Server Connection")
    ventana['background'] = bottom_color

    Label(ventana, text="Privileges Visor", bg = bottom_color, font = (None, 15)).place( x = 330, y = 15 )
    
    confirmation_var = BooleanVar()
    checkbox = Checkbutton(ventana, text="Column verbose privilege", bg = bottom_color, variable = confirmation_var)
    checkbox.place( x = 50, y = 280 )

    Label(ventana, text="Tables", bg = bottom_color, font = (None, 10)).place(x=260, y=260)
    combo_tables = ttk.Combobox( ventana )
    combo_tables.place(x=230, y=280)
    tables_insert() # This function fill the text box
    combo_tables.bind( "<<ComboboxSelected>>", fill_selector )

    Label(ventana, text="Columns", bg = bottom_color, font = (None, 10)).place(x=450, y= 260)
    combo_colum = ttk.Combobox( ventana )
    combo_colum.place( x = 420, y = 280 )

    Label(ventana, text="Schemas", bg = bottom_color, font = (None, 10)).place(x=615, y= 260)
    combo_schema = ttk.Combobox( ventana )
    combo_schema.place( x = 585, y = 280 )

    privileges_button = Button(ventana,  text = "Get privilegies", width = 15, height = 1, command = get_privileges)
    privileges_button.place(x = 350 , y = 400)
     

    execution_plan_button = Button( ventana, text = "Execution Plan View", command = endView)
    execution_plan_button.place(x = 100, y = 400)

    back_button = Button( ventana,  text = "Back", width = 10, height = 1, command = back )
    back_button.place(x = 600, y = 400) 

    ventana.mainloop()



def plan_execution_view( connection ):

    def back():
        ventana.destroy()
        privilege_view( connection )

    
    def indexes_resume ( json_result ):

        index_resume    = ""

        if ( confirmation_Var1.get() ):
            
            pool = connection.connect_to_database()
            cursor = pool.cursor()

            try:

                query = "SELECT tablename,indexname FROM pg_indexes " \
                        "WHERE schemaname = '{}' and tablename = '{}' ORDER BY tablename".format( json_result['Schema'], json_result['Relation Name'] )
                cursor.execute( query )

                row = cursor.fetchall()

                if ( len( row ) != 1 ):
                    
                    for index, index_name in enumerate ( row ):
                        index_resume += "Indice #{}: {}\n".format( index, index_name[1] )
                    
                else:
                    index_resume = "Indice de la tabla: {}\n".format( row[0][1] )

                cursor.close()
                total_resume( index_resume, json_result )

            except Exception as error:
                error_function( error )
                cursor.close()
        
        else:
            total_resume( index_resume, json_result )


    def total_resume( index_resume, json_result ):

        total_resume = "Tipo de escaneo: {}\n"\
                       "Tabla escaneada: {}\n".format( json_result['Node Type'], json_result['Relation Name']  )

        if ( len( index_resume ) != 0 ):
            total_resume += "Esquema consultado: {}\n".format( json_result['Schema'] ) + index_resume
        
        if( json_result['Node Type'] != "Seq Scan" ):
            total_resume += "Indice utilizado para el escaneo: {}".format(json_result['Index Name'])


        print ( total_resume )
        textbox_fill(total_resume)

    def textbox_fill(total_resume):
        
        response_text = Text(ventana)
        response_text.config(width=35, height=8, font=("Arial",10), padx=50, pady=15)
        response_text.place(x = 520, y = 80)
        response_text.insert(END, total_resume)
        
        os.system("py json_viewer.py test_index_plan.json")




    def     get_show_plan( ):

        pool   = connection.connect_to_database()
        cursor = pool.cursor()
        
        text_box = response_text.get("1.0","end")
       
        analyze = ""
        if(confirmation_Var2.get()):
            analyze = "analyze, "

        try:

            query = "explain (" + analyze + "format JSON, verbose " + str( confirmation_Var1.get() ) + ") " +text_box
           
            cursor.execute(query) 
            row = cursor.fetchall()[0][0]
            cursor.close()

            file = open(r"test_index_plan.json", "wt")    
            file.write(json.dumps(row[0]))
            file.close()

            json_result = json.load( open( "test_index_plan.json" ) )
            indexes_resume ( json_result['Plan'] )

            if(confirmation_Var3.get()):
                os.system("python3 json_viewer.py test_index_plan.json")


        except Exception as error: 
            error_function( error )
            cursor.close()



    ventana = Tk()
    ventana.geometry("900x350+225+110")
    ventana.title("Execution plan")
    ventana['background'] = bottom_color

    Label(ventana, text="Insert the code for view the execution plan", bg = bottom_color, font = (None, 12)).place( x = 176, y = 35 )
    
    Label(ventana, text="Execution plan resume", bg = bottom_color, font = (None, 12)).place( x = 625, y = 35 )


    response_text = Text( ventana )
    response_text.config( width=35, height=8, font=("Arial",10), padx=50, pady=15 )
    response_text.place( x = 150, y = 80)
    response_text.insert( END,"SELECT * FROM personas")


    confirmation_Var1 = BooleanVar()
    checkbox_All_plan = Checkbutton(ventana, text="Detailed plan", bg = bottom_color, variable = confirmation_Var1)
    checkbox_All_plan.place(x = 20, y = 150)

    confirmation_Var2 = BooleanVar()
    checkbox_estimated_plan = Checkbutton(ventana, text="Estimated plan", bg= bottom_color, variable = confirmation_Var2 )
    checkbox_estimated_plan.place(x = 20, y = 180)

    confirmation_Var3 = BooleanVar()
    checkbox_plan = Checkbutton(ventana, text="See tree", bg= bottom_color, variable = confirmation_Var3 )
    checkbox_plan.place(x = 20, y = 210)

    exec_button = Button( ventana,  text = "Generate plan", width = 10, height = 1, command = get_show_plan )
    exec_button.place(x = 280, y = 290 )

    back_button = Button( ventana,  text = "Back", width = 10, height = 1, command = back )
    back_button.place(x = 600, y = 290)

    Label(ventana, text="Check 'detailed plan' to see table indexes and schema", bg = bottom_color, font = (None, 12)).place( x = 300, y = 250 )



main_view_connection()