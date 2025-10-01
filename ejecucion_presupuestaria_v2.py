import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Cargar el catálogo desde el archivo Excel
dfcatalogo = pd.read_excel("Catalogo_POSTGRES.xlsx", sheet_name='catalogo', engine='openpyxl')
#dfcatalogo = dfcatalogo[["Nombre", "Objeto Gasto"]].dropna(subset=["Nombre"])
lista_items = dfcatalogo["Nombre"].dropna().unique().tolist()
op_clasificador= dfcatalogo['Descripcion'].dropna().unique()

dfprograma= pd.read_excel('programasok.xlsx', sheet_name='programas', engine='openpyxl')
op_programa = dfprograma['jurisdiccion'].dropna().unique()
#op_area= dfprograma['area'].dropna().unique()


# Inicializar almacenamiento en sesión
if "registros" not in st.session_state:
    st.session_state.registros = []

# Inicializar campos del formulario con valores por defecto
form_defaults = {
    "juridiccion": "",
    #"area": "",
    "item": lista_items[0] if lista_items else "",
    "clasificador": "",
    "cantidadrequerida":"",
    "cantidadminima":"",
    "unidadmedida":"Mensual",
    "preciounitario": 0.0,
    #"devengado_pro": 0.0,
    #"deveng_cin_ajuste": 0.0,
    "prioridad": "Alta",
    "monto": 0.0,
    "montominimo":0.0,
    #"Cantidad":0,
   
}

for key, default in form_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Sidebar para navegación
st.sidebar.title("Navegación")
pagina = st.sidebar.radio("Ir a", ["Formulario", "Gráficos"])

# Página 1: Formulario
if pagina == "Formulario":
    
    st.image("ambiente.png", use_container_width=True)
    st.title("Formulacion Presupuestaria")
    st.header('Carga de datos')

## ----------------------------------
## ACA EMPIEZAN LOS CAMPOS DE LA PAGINA
##-------------------------------------   


    st.session_state.jurisdiccion = st.selectbox("Jurisdicción:", op_programa,index=None, placeholder="Seleccionar jurisdiccion")
    
    
    #st.session_state.area = st.selectbox("Área",op_area, index=None, placeholder='Seleccionar Area')
    st.session_state.item = st.selectbox("Item", lista_items, index=None, placeholder="Seleccionar Item")

    objeto_gasto = dfcatalogo[dfcatalogo["Nombre"] == st.session_state.item]["Objeto Gasto"].values
    objeto_gasto_valor = objeto_gasto[0] if len(objeto_gasto) > 0 else "No disponible"
    st.text_input("Objeto Gasto", value=objeto_gasto_valor, disabled=True)

    clasificador= dfcatalogo[dfcatalogo['Nombre'] == st.session_state.item]['Descripcion'].values
    clasificador_valor = clasificador[0] if len(clasificador) > 0 else "No disponible"
    st.text_input('Clasificador', value=clasificador_valor , disabled=True )

    

    #st.session_state.clasificador = st.selectbox("Clasificador", op_clasificador, index=None, placeholder="Seleccionar Clasificador")
    #st.session_state.devengado_pro = st.number_input("Devengado Pro", step=0.01, value=st.session_state.devengado_pro)
    #st.session_state.deveng_cin_ajuste = st.number_input("Devengado sin ajuste (1,1)", step=0.01, value=st.session_state.deveng_cin_ajuste)
    st.session_state.cantidadrequerida= st.number_input('Cantidad Requerida', placeholder='ingresar cantidad', min_value=0, step=1)
    st.session_state.cantidadminima= st.number_input('Cantidad Minima Requerida', placeholder='ingresar cantidad', min_value=0, step=1)
    st.session_state.unidadmedida = st.selectbox("Unidad de Medida", ["Mensual", "Unidad", "Kilos","Litros","Otro"], index=["Mensual", "Unidad", "Kilos","Litros","Otro"].index(st.session_state.unidadmedida))
    st.session_state.prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"], index=["Alta", "Media", "Baja"].index(st.session_state.prioridad))
    
    #st.session_state.monto_minimo = st.number_input("Monto Mínimo", step=0.01, value=st.session_state.monto_minimo)
    st.session_state.preciounitario= st.number_input('Precio unitario estimado', placeholder='ingresar cantidad', min_value=0, step=1)

    monto= st.session_state.cantidadrequerida * st.session_state.preciounitario
    #st.session_state.monto = st.number_input("Monto", value=monto)
    st.text_input('Monto', value=monto , disabled=True )
    
    montominimo= st.session_state.cantidadminima * st.session_state.preciounitario
    #st.session_state.montominimo = st.number_input("Monto Minimo", value=montominimo)
    st.text_input('Monto Minimo', value=montominimo , disabled=True )
    st.session_state.justificacion=st.text_area('Justificacion')

    if st.button("Guardar"):
        nuevo_registro = {
            "juridiccion": st.session_state.jurisdiccion,
            #"area": st.session_state.area,
            "item": st.session_state.item,
            "objeto gasto": objeto_gasto_valor,
            "clasificador": clasificador_valor,
            #"devengado_pro": st.session_state.devengado_pro,
            #"deveng_cin_ajuste": st.session_state.deveng_cin_ajuste,
            "cantidad requerida":st.session_state.cantidadrequerida,
            "cantidad minima":st.session_state.cantidadminima,
            "unidad de medida":st.session_state.unidadmedida,
            "precio unitario":st.session_state.preciounitario,
            "monto":monto,
            "monto minimo":montominimo,
            "prioridad": st.session_state.prioridad,
            "Justificacion": st.session_state.justificacion,
        }
        st.session_state.registros.append(nuevo_registro)
        st.success("Datos guardados correctamente.")

        # Limpiar campos
        for key, default in form_defaults.items():
            st.session_state[key] = default

    # Mostrar tabla con los datos cargados
    if st.session_state.registros:
        st.subheader("Datos cargados")
        df = pd.DataFrame(st.session_state.registros)
        st.dataframe(df)

        # Exportar a Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)

        st.download_button(
            label="Exportar a Excel",
            data=buffer,
            file_name="registros.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Página 2: Gráficos
elif pagina == "Gráficos":
    st.title("Visualización de Datos")

    if not st.session_state.registros:
        st.warning("No hay datos cargados para mostrar.")
    else:
        df = pd.DataFrame(st.session_state.registros)

        st.subheader("Monto por Jurisdicción")
        fig1 = px.bar(df, x="juridiccion", y="monto", color="prioridad", title="Monto por Jurisdicción")
        st.plotly_chart(fig1)

        st.subheader("Devengado Pro vs sin ajuste")
        fig2 = px.scatter(df, x="devengado_pro", y="deveng_cin_ajuste", color="area", title="Devengado Pro vs sin ajuste")
        st.plotly_chart(fig2)
