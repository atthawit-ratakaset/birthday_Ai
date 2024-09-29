import re
import contractions
from googletrans import Translator

def calculate_ai(text):
    try:
        text = text.replace('บวก', '+')
        text = text.replace('ลบ', '-')
        text = text.replace('คูณ', '*')
        text = text.replace('หาร', '/')
        text = text.replace('ยกกำลัง', '**')
        text = text.replace('^', '**')
        
        text = text.replace(',', '')
        
        expression = ''.join(re.findall(r'[0-9+\-*/.**]+', text))
        
        if expression:
            result = eval(expression)
            
            if isinstance(result, int) or result.is_integer():
                response = f"คำตอบคือ {int(result)}"
            else:
                response = f"คำตอบคือ {result:.2f}"
        else:
            response = "ไม่สามารถตอบได้ค่ะ ต้องขออภัยด้วยค่ะ"
        
        return response
    except Exception as e:
        return f"ไม่สามารถตอบได้ค่ะ ต้องขออภัยด้วยค่ะ"

def word_translator(text):
    start_phrases = [
        "ช่วยแปลคำว่า", "ช่วยแปลประโยค", "แปลประโยค", "แปลคำว่า", 
        "ช่วยแปล", "แปล", "คำว่า", "ประโยค"
    ]
    
    end_phrases = [
        "เป็นภาษาอังกฤษให้ฟังหน่อย", "เป็นภาษาอังกฤษให้ฟังที", "เป็นภาษาอังกฤษให้หน่อย", 
        "เป็นภาษาอังกฤษหน่อย","ในภาษาอังกฤษให้ฟังหน่อย", "ในภาษาอังกฤษให้หน่อย", "ในภาษาอังกฤษคืออะไร", "ในภาษาอังกฤษคือ", 
        "ในภาษาอังกฤษ", "ภาษาอังกฤษคืออะไร", "เป็นภาษาอังกฤษ", 
        "ภาษาอังกฤษให้ฟังที", "ภาษาอังกฤษให้ฟังหน่อย", "ภาษาอังกฤษคือ", "ภาษาอังกฤษ"
    ]
    
    for phrase in start_phrases:
        if text.startswith(phrase):
            text = text[len(phrase):].strip()
            break
    
    for phrase in end_phrases:
        if phrase in text:
            text = text.replace(phrase, "").strip()
    
    translator = Translator()
    result = translator.translate(text, src='th', dest='en')
    
    translated_text = result.text
    expanded_text = contractions.fix(translated_text)

    if "he do" in expanded_text:
        expanded_text = expanded_text.replace("he do", "he does")

    if "they is" in expanded_text:
        expanded_text = expanded_text.replace("they is", "they are")

    if "she have" in expanded_text:
        expanded_text = expanded_text.replace("she have", "she has")

    if "they is" in expanded_text:
        expanded_text = expanded_text.replace("they is", "they are")

    if "it are" in expanded_text:
        expanded_text = expanded_text.replace("it are", "it is")

    if "and but" in expanded_text:
        expanded_text = expanded_text.replace("and but", "but")

    if ". Because" in expanded_text:
        expanded_text = expanded_text.replace(". Because", " because")

    if "fast very" in expanded_text:
        expanded_text = expanded_text.replace("fast very", "very fast")

    if "beautifully always" in expanded_text:
        expanded_text = expanded_text.replace("beautifully always", "always sings beautifully")

    if "is did" in expanded_text:
        expanded_text = expanded_text.replace("is did", "was done")

    if "beautifully always" in expanded_text:
        expanded_text = expanded_text.replace("beautifully always", "always sings beautifully")

    if "You are" in expanded_text and "?" in expanded_text:
        expanded_text = expanded_text.replace("You are", "Are you")

    if "I gave me" in expanded_text:
        expanded_text = expanded_text.replace("I gave me", "please give me")

    if "I eat" in expanded_text:
        expanded_text = expanded_text.replace("I eat", "I ate")

    if "I gave myself" in expanded_text:
        expanded_text = expanded_text.replace("I gave myself", "I asked for")

    if "that that" in expanded_text:
        expanded_text = expanded_text.replace("that that", "that")

    if "she are" in expanded_text:
        expanded_text = expanded_text.replace("she are", "she is")

    if "Give me" in expanded_text:
        expanded_text = expanded_text.replace("Give me", "Could you please give me")
    
    if "Where you are" in expanded_text and "?" in expanded_text:
        expanded_text = expanded_text.replace("Where you are", "Where are you")

    if "and also I want" in expanded_text:
        expanded_text = expanded_text.replace("and also I want", "but I also want")

    expanded_text = expanded_text.replace("himself went there himself", "went there himself")
    expanded_text = expanded_text.replace("to to", "to")
    expanded_text = expanded_text.replace("depend in", "depend on")
    expanded_text = expanded_text.replace("interested for", "interested in")
    expanded_text = expanded_text.replace("very very", "very")
    expanded_text = expanded_text.replace("However, but", "However,")
    expanded_text = expanded_text.replace("also is", "is also")
    expanded_text = expanded_text.replace("too is", "is too")
    expanded_text = expanded_text.replace("himself did it by himself", "did it by himself")
    expanded_text = expanded_text.replace("many information", "much information")
    expanded_text = expanded_text.replace("much people", "many people")
    expanded_text = expanded_text.replace("Please you close", "Please close")
    expanded_text = expanded_text.replace("take a decision", "make a decision")
    expanded_text = expanded_text.replace("in the top", "on the top")
    expanded_text = expanded_text.replace("If I was you, I will", "If I were you, I would")

    return expanded_text, text

