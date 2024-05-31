from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .serializer import UserSerializer, RegistroSerializer
from .models import User, Registro

from io import BytesIO
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from PIL import Image


import numpy as np

from keras.models import load_model 

from keras.preprocessing import image

from django.core.mail import send_mail
from django.http import HttpResponse

from openai import OpenAI
from django.conf import settings



from decouple import config



client = OpenAI(
    # This is the default and can be omitted
    api_key=config("OPENAI_API_KEY")
)




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegistroViewSet(viewsets.ModelViewSet):
    queryset = Registro.objects.all()
    serializer_class = RegistroSerializer

    class ResultUser(APIView):
        def get(self, request, id_user):
         try:
            registros = Registro.objects.filter(id_user=id_user)
            serializer = RegistroSerializer(registros, many=True)
            return Response(serializer.data)
         except Registro.DoesNotExist:
                return Response({'error': 'No se encontraron registros para el usuario dado'}, status=status.HTTP_404_NOT_FOUND)



class LoginView(APIView):
    def post(self, request):
        # Obtener el usuario y la contraseña proporcionados en la solicitud
        email = request.data.get('username')
        password = request.data.get('password')
        print(email)
        print(password)

        # Verificar si el usuario existe en la base de datos
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si la contraseña coincide
        if user.password == password:
            # Las credenciales son válidas
            return Response({'message': 'Inicio de sesión exitoso', 'user_id': user.id, 'name': user.name}, status=status.HTTP_200_OK)
        
        else:
            # La contraseña no coincide
            return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)


model = load_model('C:/Users/pokib/Desktop/Universidad/Decimo/Moviles/Proyecto/servicio-registro/modelo/InceptionV3(TB Chest).h5')
modelValidation = load_model('C:/Users/pokib/Desktop/Universidad/Decimo/Moviles/Proyecto/servicio-registro/modelo/validacion_imagen.h5')

class InferenceView(APIView):
    def post(self, request):
        try:
            # Obtener el user_id de los datos enviados en la solicitud
            user_id = request.data.get('user_id')
            img = request.FILES.get('image')
            imgimg = request.FILES.get('image')
            
            

            preprocessed_imageValidation = preprocess_imageValidation(img);
            img.seek(0)
           
            
            # Intenta hacer la predicción
            predictions = modelValidation.predict(np.expand_dims(preprocessed_imageValidation, axis=0))
            print(predictions)
            class_names = ['Radiografias', 'Variadas']

            if predictions[0][0] > 0.5:
                print("Variadas")
                indice_clase_mayor_probabilidad = "Variadas"
            else:
                print("Radiografia")
                indice_clase_mayor_probabilidad = "Radiografia"

            # Procesar según la clase con la mayor probabilidad
            if indice_clase_mayor_probabilidad == "Radiografia":
                
                result_tb=0
                result_no_tb=0
                
                preprocessed_image = preprocess_image(img);
               
              
                predictionss = model.predict(preprocessed_image)
               
                print(predictionss[0])
               
             
                    
                   
                
                result_tb = predictionss[0]
                result_no_tb = 1- predictionss[0]
                
                print (result_tb) 
              
                if result_tb > result_no_tb:
                    result = True
                
                if result_no_tb > result_tb:
                    result = False
                    

                fecha = datetime.now()

                
                result_tb1 = round(float(result_tb) * 100, 2)
                result_no_tb1 = round(float(result_no_tb) * 100, 2)
               
                print("User ID:",user_id)
                print("Fecha:", fecha)
                print("Tuberculosis:",result)
                print("Porcentaje Tuberculosis:",result_tb)
                print("Porcentaje Normal:", result_no_tb)
                
                
                user_instance = User.objects.get(id=user_id)
                
                print("User Instance:", user_instance)
                
                # Crea una instancia de Registro con los datos proporcionados
                registro = Registro.objects.create(
                    date=fecha,
                    tuberculosis=result,
                    prct_tuberculosis=result_tb1,
                    prct_no_tuberculosis=result_no_tb1,
                    id_user=user_instance
                    
                )

            # Devolver una respuesta exitosa con el user_id recibido
                return Response({'result': result, 'result_tb': result_tb1, 'result_no_tb': result_no_tb1  }, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'La imagen no es una radiografia'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as ex:
            return Response({'message': 'Error en el procesamiento de la imagen2'}, status=status.HTTP_401_UNAUTHORIZED)





def preprocess_imageValidation(image_file):
    try:
        img_stream = BytesIO(image_file.read())

        img = image.load_img(img_stream, target_size=(300, 300))

        img_array = image.img_to_array(img)

        img_array /= 255.0
        return img_array
    except Exception as ex:
        # Manejar cualquier excepción que ocurra durante el preprocesamiento de la imagen
        raise Exception('Error en el preprocesamiento de la imagen1: {}'.format(str(ex)))




def preprocess_image(image_file):
    try:
        img_stream = BytesIO(image_file.read())
        img = image.load_img(img_stream, target_size=(299, 299))

        img_array = image.img_to_array(img)

        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        return img_array
    except Exception as ex:
        # Manejar cualquier excepción que ocurra durante el preprocesamiento de la imagen
        raise Exception('Error en el preprocesamiento de la imagen1: {}'.format(str(ex)))

def obtener_fecha():
    # Obtener la fecha actual
    fecha_actual = datetime.now()

    # Obtener solo la fecha (sin la hora)
    fecha_sin_hora = fecha_actual.date()

    # Almacenar la fecha en una variable
    mi_fecha = fecha_sin_hora

    # Devolver la fecha como parte de la respuesta
    return mi_fecha



class ReportView(APIView):
    def post(self, request):
        try:
            # Obtener datos de la solicitud
            data = request.data
            print(data)
            
            # Extraer datos del paciente
            paciente = data.get("paciente", {}).get("nombre")
            email = data.get("paciente", {}).get("email")
                
            print(paciente, email)

           

            # Crear el prompt para la API de OpenAI
            prompt = (
                f"Obtuve estos resultados después de realizar un análisis de tuberculosis en la fecha de cada examen como esta en los datos "
                f"Es un examen pulmonar con radiografías de tórax utilizando un modelo de CNN al paciente {paciente}. "
                f"Datos obtenidos: {data}. Realizame un reporte que contenga: "
                f"Nombre paciente "
                f"Análisis de resultados con fechas "
                f"Dame algun analisis de los resultados detallando un poco pero no recomendaciones."
            )

           
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt}
                ]
                )

            generated_text = response.choices[0].message.content
            
            print(generated_text)

            # Enviar el mensaje por correo electrónico
            send_mail(
                subject='Reporte de OpenAI',
                message=f'Hola {paciente},\n\nAquí está el reporte generado por OpenAI:\n\n{generated_text}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email]
            )

            return HttpResponse('Correo enviado exitosamente')

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)