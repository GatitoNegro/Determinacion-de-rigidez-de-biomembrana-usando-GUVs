import streamlit as st
import numpy as np  # procesamiento matricial
import matplotlib.pyplot as plt  # para mostrar imagenes
import pandas as pd
import imageio as iio
import cv2

def binarizar(imagen, n):
  median = cv2.medianBlur(imagen, n)#filtro de la mediana con kernel 
  binarizada = cv2.adaptiveThreshold (median, 255 , cv2.ADAPTIVE_THRESH_GAUSSIAN_C , cv2.THRESH_BINARY ,5,0) 
  binarizadaf =cv2.medianBlur(binarizada,n) 
  return binarizadaf

def calcularcentro(bin):
    M1 = cv2.moments(bin)
    if M1["m00"]==0: M1["m00"]=1
    cX1 = int(M1["m10"] / M1["m00"])
    cY1 = int(M1["m01"] / M1["m00"])
    # put text and highlight the center
    coord= (cX1, cY1)
    return coord

def calcularcontorno(binarizadam):
    contorno,hierarchy=cv2.findContours(binarizadam,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    j=0
    while len(contorno)>2:
        if j==len(contorno):
            print('error, hay mas de 2 contornos de tamaño considerable')
            break
        else:
            if  contorno[j].shape[0]<130:
                del(contorno[j])
            else:
                j=j+1
    return contorno

def dibujarcontorno(cont,a):
    dibujo =np.zeros((dimensiones[1],dimensiones[2]))
    cv2.drawContours(dibujo, cont, a, 255, 2)
    return dibujo

def calcularpolares(cont,cm):
    radiocomponentes=cont-cm
    radio=pow((pow(radiocomponentes,2).sum(axis=-1)),1/2).round(2) #Axis no entendi
    angulo=(np.arctan2(radiocomponentes[:,:,1], radiocomponentes[:,:,0]) * 180 / np.pi).round(2)
    pol=np.append(angulo,radio,axis=1)
    return pol

def discretizar(pol,v):
  n=-1 ##discretiza los valores del angulo con escalon de v grados
  for i in pol[:,0]: 
    n=n+1
    encontrado=0
    ma=180
    mi=180-(360/v)
    while encontrado==0:
      if i<=ma and i>mi:
        pol[n,0]=ma
        encontrado=1
      ma=ma-(360/v)
      mi=mi-(360/v)
  pol_ord=pol[np.lexsort(np.fliplr(pol).T)] #OREDENAMOS

  discretizada=np.zeros((v,2))
  c=-1
  for i in discretizada[:,0]:
    c=c+1
    discretizada[c,0]=180-(360/v)*c
  discretizada_ord =np.sort(discretizada,axis=0)

    ##promedia los radios con el mismo angulo
  k=0 #recorrera matriz original
  u=0 #acumulador valores
  l=1 #recorrera matriz nueva
  o=0 #cuenta valores iguales para poder promediar
  e=0 #cuenta errores de falta de radios para algun angulo se utilizara a modo de bandera
  pol_ord=np.append(pol_ord, [[555,555]], axis=0)#se agrega un valor aleatorio al final, para indicar el final.
  while l<=v:
    while pol_ord[k,0]==-180+(l*(360/v)):
      u=u+pol_ord[k,1]
      o=o+1
      k=k+1
    if o==0:
      #print(f"error, no hay valores para el angulo {discretizadaINord[l-1,0]} grados")
      o=1 #evita div por 0
      e=e+1
    discretizada_ord[l-1,1]=u/o
    l=l+1
    o=0
    u=0

  if e!=0 and e<20:
    #ARREGLA FALTA DE ANGULOS 
    m=0
    while m<len(discretizada_ord):
      if discretizada_ord[m,1]==0:
        if m==0:
          discretizada_ord[m,1]=(discretizada_ord[(len(discretizada_ord))-1,1]+discretizada_ord[m+1,1])/2
          #Si la primera punta no tiene valor, entonces saca promedioentre el sig elemento y la otra punta
        if m==len(discretizada_ord)-1==0:
          discretizada_ord[m,1]=(discretizada_ord[0,1]+discretizada_ord[m-1,1])/2
        #Si la otra punta no tiene elemento saca promedio entre el penultimo elemento y la primera punta
        discretizada_ord[m,1]=(discretizada_ord[m-1,1]+discretizada_ord[m+1,1])/2
        #Si el cero esta en cualquier otra parte saca el promedio entre el anterior y el siguiente elemento.
      m=m+1

  return discretizada_ord

def calcularcoeficientes(discre):
    An=np.zeros([50])
    for n in range(1,51):
      cos=np.cos(n*discre[:,0]*np.pi/180)
      cos_radio=cos*discre[:,1]
      sumatoria=0
      for h in range(cos_radio.shape[0]):
        suma=cos_radio[h]+cos_radio[(h+1)%cos_radio.shape[0]]
        resta=discre[(h+1)%cos_radio.shape[0],0]*np.pi/180-discre[h,0]*np.pi/180
        if (h+1)%cos_radio.shape[0]==0:
          resta=resta+2*np.pi
        producto=suma*resta
        sumatoria=sumatoria+producto
      An[n-1]=sumatoria/(2*np.pi)

    Bn=np.zeros([50])
    for n in range(1,51):
      sin=np.sin(n*discre[:,0]*np.pi/180)
      sin_radio=sin*discre[:,1]
      sumatoria=0
      for h in range(sin_radio.shape[0]):
        suma=sin_radio[h]+sin_radio[(h+1)%sin_radio.shape[0]]
        resta=discre[(h+1)%sin_radio.shape[0],0]*np.pi/180-discre[h,0]*np.pi/180
        if (h+1)%sin_radio.shape[0]==0:
          resta=resta+2*np.pi
        producto=suma*resta
        sumatoria=sumatoria+producto
      Bn[n-1]=sumatoria/(2*np.pi)
    return An,Bn

header = st.container()
with header:
    st.title("GUVis")
    col1, col2 = st.columns(2)
    with col1:
        st.text("Se aceptan en formato .avi o .mp4")
        uploader= st.file_uploader("Subir video", type=["avi", "mp4"])
    
    if uploader is not None:
        #file_details = {'filename':uploader.name, 'file type':uploader.type}
        #st.write (file_details)
        with col2:
            #st.subheader("Video subido")
            st.video(uploader)

        video_bytes = uploader.read()

        with open("video.mp4", "wb") as fp: #abrimos un contenedor donde escribimos el video    
            fp.write(video_bytes)

        lector = cv2.VideoCapture ('video.mp4')
        width = int(lector.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(lector.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frames = int(lector.get(cv2.CAP_PROP_FRAME_COUNT))
        dimensiones = (frames, height, width)
        video_np = np.zeros(dimensiones)

        st.sidebar.title("Barra de ingresos")
        st.sidebar.text("Video subido")
        x = st.sidebar.slider('Imagen en el video', 0, frames-1, 1)
        st.sidebar.write('Numero de frame:', x)
                
        n=0
        while lector.isOpened():
            ret, frame = lector.read()
            if ret==True:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                video_np[n,:,:]=gray
                n=n+1
            else:
                break 
        video_np = video_np.astype(np.uint8)
        col4, col5, col6 = st.columns(3)
        with col4:
            #st.subheader("Grises")
            st.image(video_np[x], caption=f'Frame numero {x}', clamp=True)
        st.sidebar.title("Tamaño de ventanas")
        kernel1 = st.sidebar.slider('Ventana 1', min_value=3, max_value=11, step=2)
        kernel2 = st.sidebar.slider('Ventana 2', min_value=3, max_value=11, step=2)
        mediana = cv2.medianBlur(video_np[x],int(kernel1))
        binarizada1 = cv2.adaptiveThreshold (mediana , 255 , cv2.ADAPTIVE_THRESH_GAUSSIAN_C , cv2.THRESH_BINARY ,7,-0) 
        binarizada2 = cv2.medianBlur(binarizada1, int(kernel2))#filtro de la mediana con kernel 
        with col5:
            #st.subheader("Filtros")
            st.image(binarizada2, caption=f'Frame numero {x} binarizado', clamp=True)
        contorno,hierarchy=cv2.findContours(binarizada2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
       
        