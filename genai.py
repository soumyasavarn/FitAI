import google.generativeai as genai
import os

GOOGLE_API_KEY = os.environ.get("GOOGLE_API")
#source(for getting API): https://ai.google.dev/?utm_source=google&utm_medium=cpc&utm_campaign=brand_core_brand&gad_source=1

def get_calories(img):
    
    print (img)
    print(type(img))
    genai.configure(api_key=GOOGLE_API_KEY) #Configuring the genai 
    # def get_calories(image):
    try: 
        model = genai.GenerativeModel('gemini-pro-vision') #Choosing the image to text model
        from datetime import datetime
        current_date_time = datetime.today()
        current_day = current_date_time.strftime("%A")
        print (current_day)
        prompt = "I am providing the mess menu of the week and today is " + current_day + ". Go through the all the food items listed on" + current_day + "and calculate the total calories consumed for the day. Remember I just need an integer as an output which is the total calories calculated."
        total_calories = 0
        try: 
            for i in range (0,2):
                response = model.generate_content([prompt,img]) #trying to get the response from the model
                model_answer = "Error fetching the response !" #Initialising the variable as Error message 
                # print (model_answer)
                #Extracting the answer as by default Google's response is a complicated data structure which stores all the info
                for candidate in response._result.candidates:
                        parts = candidate.content.parts
                        for part in parts:
                            model_answer = part.text 
                
                total_calories += int(model_answer)
                print (total_calories)
            return ( int(total_calories/2) )
                
        except:
            print ("Error fetching the response !")
            return -1
    except:
        print ("Error loading the image !")
        return -1


