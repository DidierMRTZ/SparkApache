from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import pandas as pd
import re
from collections import OrderedDict
from dash import dash_table as dt
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
import numpy as np
import dash_bootstrap_components as dbc


"""------------------------------------------ START Search ZD110----------------------------------------------------"""
def Search_ZSD110(Transsaccion,variant,provision):
    session.StartTransaction(Transsaccion)
    session.findById("wnd[0]/tbar[1]/btn[17]").press()
    Varians_ZSD110=session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
    Rows_Varians_ZSD110=Varians_ZSD110.RowCount
     # List Variants
    List_Varian_ZSD110=[Varians_ZSD110.GetCellValue(i,"VARIANT") for i in range(0,Rows_Varians_ZSD110)] 
    indice=[indice for indice, dato in enumerate(List_Varian_ZSD110) if dato == variant]
    Varians_ZSD110.selectedRows = indice[0]
    session.findById("wnd[1]/tbar[0]/btn[2]").press()
    session.findById("wnd[0]/usr/ctxtPA_LAYOU").text = provision
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    tabla_zsd110=session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell")     #Select table cont
    return(tabla_zsd110)


"""----------------------------------------------CLEAN COLUMN AND DATA-----------------------------------------------------------"""
def Clean_Columns(List):
    Set_Columns=[i.strip() for i in List.columns]   #Alert in list
    clean_column=[i if "Unnamed" in i else None for i in List.columns]
    clean_column = list(filter(lambda x: x is not None, clean_column)) 
    List=List.set_axis(Set_Columns, axis=1).drop(clean_column,axis=1)  #Drop Unammed: 0
    return(List)

"""------------------------------------------FUNCION PARA CAMBIAR A NUMEROS-------------------------------------------------------"""

def Clean_num(x):
    x = float(str(x).strip().replace(',',''))
    return(x)

"""------------------------------------------FUNCION PARA COMPLETAR los 10 con 00 al inicio---------------------------------------"""
def Complete_00(lista):
    Nueva_Lista_Ordenes=[]
    for i in lista:
        while len(str(i))<10:
            i="0"+i
            # print(len(str(i)),i)
        Nueva_Lista_Ordenes.append(str(i))
    return(Nueva_Lista_Ordenes)

def default_column(default_columns,dataframe):     #Parametros (default_columns: Columnas predeterminadas,dataframe:)
    diccionay_default_column={}
    if len(default_columns)==len(dataframe.columns):
        for i in range(0,len(default_columns)):
            diccionay_default_column[dataframe.columns[i]]=default_columns[i]   
        dataframe=dataframe.rename(columns=diccionay_default_column)   #Remplazo las columnas con las de default
    else:
        None   #asumo columnas originales como estandar
    return(dataframe)


# Ecluir Agenda de pedidos exito

def Datos_Agenda(data_pedido,Agenda):   #(data_pedido: columna dataframe a transformar, Agenda: Datos a encontrar)
    Exluidos_Entrega=set()
    for i in data_pedido:
        if (str(i)[:4] in Agenda) or (str(i)[:3] in Agenda):
            Exluidos_Entrega.add(i)
    return(Exluidos_Entrega)


def Search_agenda(data_Pedidos,agenda):
    conjunto_agenda=set()
    for i in data_Pedidos:
        if re.findall("(\d*)-",str(i))!=[] and (re.findall("(\d*)-",str(i))[0] in agenda):
            conjunto_agenda.add(i)
    return(conjunto_agenda)



default_column_Canal01_Pendientes=['Can.distr.', 'Denomin.', 'Seccion', 'Estado', 'Solic.', 'Nombre',
       'Pedido', 'Clase Pedi', 'Creado el', 'Pedido.1', 'Posición', 'Material',
       'Vlr.Neto P', 'Moneda', 'Cantidad P', 'Cantidad C', 'UM venta',
       'Vlr.Neto C', 'Status Glo', 'Status Tot', 'Status Ent', 'Status Ent.1',
       'Status Ent.2']  


default_column_Canal01_Entregado=['Can.distr.', 'Denomin.', 'Seccion', 'Estado', 'Solic.', 'Nombre',
       'Entrega', 'Posicion E', 'F.Creacion', 'Pedido', 'Clase Pedi',
       'F.Creacion.1', 'Pedido.1', 'Posicion P', 'Material', 'Moneda',
       'Cantidad E', 'UM venta', 'Valor Neto', 'StTotPick.', 'StatGlWM',
       'StTotMovMe', 'Stat.fact.', 'Status PT']

default_column_Pedidos=['OrgVt', 'CDis', 'BqEn', 'Solic.', 'PrimFeEntr', 'ÚltEntrega',
       'FePrefEnt.', 'ClVt', 'Valor neto', 'Mon.', 'Doc.venta', 'ST',
       'Solicitante', 'Nº pedido cliente', 'Descrip.breve', 'Nº de cliente 1',
       'Contador de pedidos', 'Dirección', 'Barrio', 'Población', 'Teléfono']


"""----------------------------------------------LEER ARCHIVOS--------------------------------"""
#Data Pendientes
Canal01_Pendiente=pd.read_csv("Archivos_CSV\\Canal01_PEN.txt",skiprows=1,delimiter="\t")
Canal01_Pendiente=Clean_Columns(Canal01_Pendiente)
Canal01_Pendiente=default_column(default_column_Canal01_Pendientes,Canal01_Pendiente)

#Dta Entregados
Canal01_Entregado=pd.read_csv("Archivos_CSV\\Canal01_ENT.txt",skiprows=1,delimiter="\t")
Canal01_Entregado=Clean_Columns(Canal01_Entregado)
Canal01_Entregado=default_column(default_column_Canal01_Entregado,Canal01_Entregado)

"""""-------------------------------------------Limpio los datos-----------------------------------"""
Canal01_Entregado['Valor Neto']=Canal01_Entregado['Valor Neto'].apply(lambda x: Clean_num(x))
Canal01_Entregado['Cantidad E']=Canal01_Entregado['Cantidad E'].apply(lambda x: Clean_num(x))


"""-----------------Datos descriptivos de interes-----------------------------------"""
#Lineas Totales
Lines_Canal01_Pendiente=len(Canal01_Pendiente)
Lines_Canal01_Entregado=len(Canal01_Entregado)


"""------------------------Optener datos de Agenda_Exito y Cencosub------------------"""

#Agenda Exito y Cencosub
Agenda_Exito=["0085","0020","0146","0149","0050","0138","0045"]
Agenda_Cencosub=["93","122","127","95","60"]

"""-----------------------------Aplico filtro en Agenda exito----------------------------------"""

Filtro_Agenda_Exito=Datos_Agenda(Canal01_Entregado['Pedido.1'],Agenda_Exito)
Filtro_Agenda_Cencosub=Search_agenda(Canal01_Entregado["Pedido.1"],Agenda_Cencosub)


"""------------------------------Canal 01 Entrega con y sin agenda Exito-----------------------"""
Filtro_Canal01_Entregado_Exito=(Canal01_Entregado['Pedido.1'].isin(Filtro_Agenda_Exito))   #Excluyo con ~
Canal01_Entregado_Agenda_Exito=Canal01_Entregado.loc[Filtro_Canal01_Entregado_Exito].reset_index(drop=True)
Canal01_Entregado_Sin_Agenda_Exito=Canal01_Entregado.loc[~Filtro_Canal01_Entregado_Exito].reset_index(drop=True)


"""------------------------------Canal 01 Entrega con y sin agenda Cencosub-----------------------"""
Filtro_Canal01_Entregado_Cencosub=(Canal01_Entregado['Pedido.1'].isin(Filtro_Agenda_Cencosub))   #Excluyo con ~
Canal01_Entregado_Agenda_Cencosub=Canal01_Entregado.loc[Filtro_Canal01_Entregado_Cencosub].reset_index(drop=True)
Canal01_Entregado_Sin_Agenda_Cencosub=Canal01_Entregado.loc[~Filtro_Canal01_Entregado_Cencosub].reset_index(drop=True)



#Canal01_Entregado_Exluido.pivot_table(,,['Material', 'Valor Neto'])

Table_dinamica_Exito_entrega=Canal01_Entregado_Agenda_Exito.pivot_table(index=['Pedido.1','Clase Pedi'],aggfunc={'Material':'count','Cantidad E':sum,'Valor Neto':sum}).reset_index()
Lineas_table_dinamica_Exito_entrega=sum(Table_dinamica_Exito_entrega["Material"])


Table_dinamica_Cencosub_entrega=Canal01_Entregado_Agenda_Cencosub.pivot_table(index=['Pedido.1','Clase Pedi'],aggfunc={'Material':'count','Cantidad E':sum,'Valor Neto':sum}).reset_index()
Lineas_table_dinamica_Cencosub_entrega=sum(Table_dinamica_Cencosub_entrega["Material"])

"""----------------------------------------------------------------Buscar en ZSD037---------------------------------------"""

"""------------------------------------------------SAVE ZSD037--------------------------------------------"""

Name_ZSD037="Pedidos pendientes"



# ZSD110 FIRME
url_ZSD037_Pedidos="Archivos_CSV\\"+str(Name_ZSD037)+".txt"

Data_ZSD110_Pedidos_Pendientes=pd.read_csv(url_ZSD037_Pedidos,skiprows=5,delimiter="\t")
Data_ZSD110_Pedidos_Pendientes=Clean_Columns(Data_ZSD110_Pedidos_Pendientes)
Data_ZSD110_Pedidos_Pendientes=default_column(default_column_Pedidos,Data_ZSD110_Pedidos_Pendientes)

"""-----------------------------------------------Limpieza de datos-------------------------------------"""


Data_ZSD110_Pedidos_Pendientes=Data_ZSD110_Pedidos_Pendientes[Data_ZSD110_Pedidos_Pendientes['Nº pedido cliente'].notnull()]   #Elimina filas nulas
Data_ZSD110_Pedidos_Pendientes['Nº pedido cliente']=Data_ZSD110_Pedidos_Pendientes['Nº pedido cliente'].astype(int).astype(str)

#Dataframe de interes
Data_ZSD110_Pedidos_Pendientes_Fecha=Data_ZSD110_Pedidos_Pendientes[['Nº pedido cliente','PrimFeEntr','ÚltEntrega']].drop_duplicates()
Remplace_Pedidos_Pendientes_Fecha=Complete_00(Data_ZSD110_Pedidos_Pendientes_Fecha['Nº pedido cliente'])  #Se pasa una columna pero en formato Str 
Data_ZSD110_Pedidos_Pendientes_Fecha['Nº pedido cliente']=Remplace_Pedidos_Pendientes_Fecha


Tabla_Agenda_Exito=pd.merge(Data_ZSD110_Pedidos_Pendientes_Fecha,Table_dinamica_Exito_entrega,how="right",left_on="Nº pedido cliente",right_on="Pedido.1")[['Nº pedido cliente', 'PrimFeEntr', 'ÚltEntrega',
       'Clase Pedi', 'Cantidad E', 'Material', 'Valor Neto']]

Agenda_name_Exito={"0085":"FUNZA","0020":"VEGAS","0146":"BARRANQUILLA","0149":"BUCARAMANGA","0050":"CALI","0138":"PEREIRA","0045":"SURTIMAYORISTAS"}



Tabla_Agenda_Exito["Plataforma"]=Tabla_Agenda_Exito["Nº pedido cliente"].apply(lambda x: Agenda_name_Exito[re.findall("("+"|".join(list(Agenda_name_Exito.keys()))+")",x)[0]] if re.findall("("+"|".join(list(Agenda_name_Exito.keys()))+")",x)!=[] else x)









"""------------------------------------------------SAVE ZSD037--------------------------------------------"""

Name_ZSD037="Pedidos entrega"



# ZSD110 FIRME
url_ZSD037_Entrega="Archivos_CSV\\"+str(Name_ZSD037)+".txt"

Data_ZSD110_Pedidos_Entrega=pd.read_csv(url_ZSD037_Entrega,skiprows=5,delimiter="\t")
Data_ZSD110_Pedidos_Entrega=Clean_Columns(Data_ZSD110_Pedidos_Entrega)
Data_ZSD110_Pedidos_Entrega=default_column(default_column_Pedidos,Data_ZSD110_Pedidos_Entrega)


#Aqui arreglar.........................

Data_ZSD110_Pedidos_Entrega=Data_ZSD110_Pedidos_Entrega[Data_ZSD110_Pedidos_Entrega['Nº pedido cliente'].notnull()]   #Elimina filas nulas

try:
    Data_ZSD110_Pedidos_Entrega['Nº pedido cliente']=Data_ZSD110_Pedidos_Entrega['Nº pedido cliente'].astype(int).astype(str)
except:
    Data_ZSD110_Pedidos_Entrega['Nº pedido cliente']=Data_ZSD110_Pedidos_Entrega['Nº pedido cliente'].astype(str)



#Dataframe de interes
Data_ZSD110_Pedidos_Entrega_Fecha=Data_ZSD110_Pedidos_Entrega[['Nº pedido cliente','PrimFeEntr','ÚltEntrega']].drop_duplicates()

Tabla_Agenda_Cencusub=pd.merge(Data_ZSD110_Pedidos_Entrega_Fecha,Table_dinamica_Cencosub_entrega,how="right",left_on="Nº pedido cliente",right_on="Pedido.1")[['Nº pedido cliente', 'PrimFeEntr', 'ÚltEntrega',
       'Clase Pedi', 'Cantidad E', 'Material', 'Valor Neto']]

Agenda_name_Cencosub={"93-":"MEDELLIN","122-":"BARRANQUILLA","127-":"BUCARAMANGA","95-":"CALI","60-":"BOGOTA"}


Tabla_Agenda_Cencusub["Plataforma"]=Tabla_Agenda_Cencusub["Nº pedido cliente"].apply(lambda x: Agenda_name_Cencosub[re.findall("\d*-",x)[0]] if re.findall("\d*-",x)[0] in list(Agenda_name_Cencosub.keys()) else None)

""""
"""""
""""
"""





Tabla_Agenda_Exito
Tabla_Agenda_Cencusub


data=np.array([["Exito",2,3],["Cencosub",4,5]])

df3=pd.DataFrame(data,index=["Exito","Cencosub"],columns=["Cliente","ZVMI","FIRME"])


        
def Create_Table(Table,Name_id):
    """
    - Table: Dataframe referencia a tabla
    - Name_id: Id de la tabla
    - Alias_libreria: Libreria Dash dash_table as dt
    """ 
    Tabla=dt.DataTable(
            id=Name_id,
            columns=[{"name": i, "id": i} for i in Table.columns],
            data=Table.to_dict("records"),
            style_data={
            'fontSize':'11px'
            },
            style_table={
                'margin': '0 auto',
                'border': '1px solid black',
                'borderCollapse': 'collapse'
            },
            style_header={
                'fontSize':'11px',
                'backgroundColor': '#4074D5',
                'fontWeight': 'bold',
                'border': '1px solid black'
            },
            style_cell={
                'textAlign': 'center',
                'border': '1px solid black',
                'padding': '5px',
                'width': '20px'
            },
            )
    return(Tabla)

def Create_Dropdown(Column_Table,Estados,Name_id):
        Dropdown=dcc.Dropdown(
                        id=Name_id,
                        options=[{"label": st, "value": st} for st in Estados],
                        placeholder="-Select a State-",
                        multi=True,
                        value=Column_Table.unique())
        return(Dropdown)


app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
states_clase_pedido_Exito = Tabla_Agenda_Exito['Clase Pedi'].unique().tolist()
states_clase_pedido_Cencosub  =Tabla_Agenda_Cencusub['Clase Pedi'].unique().tolist()
states_clase_plataforma_Exito = Tabla_Agenda_Exito['Plataforma'].unique().tolist()


Pague_1 = html.Div(children=[
    html.Div(className="row", children=[
        html.Div(className="col-md-6", children=[
            html.H3("Consolidado"),
            html.Div(children=[
                Create_Table(df3,"Consolidado_Agenda_Exito_Cencosub"),
            ]),
        ]),
    ]),
    html.Div(className="row justify-content", children=[
        html.Div(className="col-md-6 w-50 mx-auto", children=[
            html.Div(className="row justify-content", children=[
                html.Div(className="col-md-6 w-50 mx-auto", children=[
                    html.Label(['Clase Pedido'], style={'font-weight': 'bold', "text-align": "center"}),
                    Create_Dropdown(Tabla_Agenda_Exito['Clase Pedi'],states_clase_pedido_Exito,"filter_dropdown_Clase_Pedido_E"),  #Creamos Dropsown
                ]),
                html.Div(className="col-md-6 w-50 mx-auto", children=[
                    html.Label(['Plataforma'], style={'font-weight': 'bold', "text-align": "center"}),
                    Create_Dropdown(Tabla_Agenda_Exito['Plataforma'],states_clase_plataforma_Exito,"filter_dropdown_Plataforma_E"),   #Creamos Dropdown
                ]),
            ]),
            html.Br(),
            html.H3("Tabla entrega EXITO"),
            Create_Table(Tabla_Agenda_Exito,"Tabla_Agenda_Exito"),    #Crear Tabla_Agenda_Exito                                      
        ]),    
        html.Div(className="col-md-6 w-50 mx-auto", children=[
            html.Label(['Clase Pedido'], style={'font-weight': 'bold', "text-align": "start"}),
            Create_Dropdown(Tabla_Agenda_Cencusub['Clase Pedi'],states_clase_pedido_Cencosub,"filter_dropdown_Clase_Pedido_CEN"),
            html.Br(),
            html.H3("Tabla entrega CENCOSUB"),
            Create_Table(Tabla_Agenda_Cencusub,"Tabla entrega CENCOSUB"),
        ]),   
    ]),
])




app.layout = html.Div([
    html.H1('Reporte Disnal'),
    dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='Tab One', value='tab-1-example-graph', children=[Pague_1]),
        dcc.Tab(label='Tab Two', value='tab-2-example-graph'),
    ]),
])



@app.callback(
    Output("Tabla_Agenda_Exito", "data"),
    Output("Tabla entrega CENCOSUB", "data"), 
    Output("Consolidado_Agenda_Exito_Cencosub", "data"), 
    Input("filter_dropdown_Clase_Pedido_E", "value"),
    Input("filter_dropdown_Plataforma_E", "value"),
    Input("filter_dropdown_Clase_Pedido_CEN", "value"),
    Input('tabs-example-graph', 'value'),
)

def display_table(state,s,states,tab):
    if tab == 'tab-1-example-graph':
        dff = Tabla_Agenda_Exito[Tabla_Agenda_Exito['Clase Pedi'].isin(state) | Tabla_Agenda_Exito['Plataforma'].isin(s)]
        dff2 = Tabla_Agenda_Cencusub[Tabla_Agenda_Cencusub['Clase Pedi'].isin(states)]
        df3["ZVMI"][0]=dff["Cantidad E"].sum()
        df3["ZVMI"][1]=dff2["Cantidad E"].sum()
        df3["FIRME"][0]=Lineas_table_dinamica_Exito_entrega-len(dff)
        df3["FIRME"][1]=Lineas_table_dinamica_Cencosub_entrega-len(dff2)
        dff3=df3
        return dff.to_dict("records"),dff2.to_dict("records"),dff3.to_dict("records")
    elif tab == 'tab-2-example-graph':
        return None


app.run(host='0.0.0.0', port=8000, debug=False)
