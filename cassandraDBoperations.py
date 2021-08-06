from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json

class cassandraDBManagement:

    def __init__(self):
        self.cloud_config = {
            'secure_connect_bundle': 'D:\secure-connect-test.zip'
        }
        self.auth_provider = PlainTextAuthProvider('rWBkAlIgfcvLJxvhXyfHDGyr',
                                              'L1eqqevc4xh0X7Jt+2zSZ2mrwSZclSkdwWCmn7Ra82GAefe7xf,i8,TA+1,za_lI8qFiyFW_LJAwmxQpZA.Zo-ctWc8i2h5m3rp9GB06crcXaklWJAEytP3yLJibzZr7')
        self.cluster = Cluster(cloud=self.cloud_config, auth_provider=self.auth_provider)

        self.session = self.cluster.connect()

        self.keyspace = 'ineuron'

    def isKeyspacePresent(self, keyspace):
        try:
            if keyspace in self.cluster.metadata:
                self.keyspace = keyspace
                return True
            else:
                return False
        except Exception as e:
            raise Exception("(iskeyspacePresent): Failed on checking if the keyspace is present or not \n" + str(e))

    def isTablepresent(self, table, keyspace):
        try:
            row = self.session.execute(f"SELECT table_name FROM system_schema.tables WHERE keyspace_name='{keyspace}';").all()
            table_list = [i.table_name for i in row]
            if table.lower() in table_list:
               return True
            else:
                return False
        except Exception as e:
              print("error: (isTablePresnt) ", e)

    def CreateTable(self,table_name, keyspace):
        try:
            column_string =  'product_name text, product_searched text, price text, offer_details text, discount_percent text, EMI text, rating text, comment text, customer_name text, review_age text'
            row = self.session.execute(f"CREATE TABLE {keyspace}.{table_name} ({column_string}, PRIMARY KEY(product_searched, product_name ,customer_name,comment, rating))").one()


        except Exception as e:

            print("error: (createtable)", e)




    def isproductavailable(self, search_string, table):

        try:
            if self.isTablepresent(table = table, keyspace= self.keyspace):
                row = self.session.execute(f"select product_searched from {self.keyspace}.{table} where product_searched = '{search_string}';").all()
                if row != []:

                    return True
                else:

                    return False
            else:

                self.CreateTable(table_name= table, keyspace = self.keyspace)
                return False
        except Exception as e:

            print("error: (isproductavaailable) ", e)

    def getallproductdata(self, search_string, table):
        try:
            data = []
            row = self.session.execute(f"select json * from {self.keyspace}.{table} where product_searched = '{search_string}'").all()
            for i in range(len(row)):
                data.append(json.loads(row[i][0]))
            return data
        except Exception as e:
            print("error: (getallproductdata)", e)

    def insertdata(self, record, table):
        try:
            data = json.dumps(record)
            row = self.session.execute(f"""INSERT INTO {self.keyspace}.{table} JSON '{data}';""")
        except Exception as e:
            print("error: (insertdata)", e)


