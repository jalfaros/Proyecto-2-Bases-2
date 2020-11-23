import psycopg2

class Connection:
    

    def __init__( self, database, server, user, password, port ):

        self.server   = server
        self.database = database
        self.user     = user
        self.password = password
        self.port     = port


    def connect_to_database( self ):

        try:
            conn =  psycopg2.connect(   host        = self.server,
                                        database    = self.database,
                                        user        = self.user,
                                        password    = self.password,
                                        port        = self.port )
            return conn
        except( Exception, psycopg2.Error ) as error:
            print( "Unable to connect to database, please check and try again ", error )
            return False

            

