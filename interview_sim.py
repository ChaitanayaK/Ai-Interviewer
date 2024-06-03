import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from dotenv import load_dotenv
import base64

load_dotenv()

client = OpenAI()

number_of_questions = 10

def openai_tts(text, model="tts-1", voice="alloy"):
    response = client.audio.speech.create(model=model, voice=voice, input=text)
    audio_data = response.content 

    b64 = base64.b64encode(audio_data).decode()
    md = f"""
                    <style>
            #hidden-audio {{
                display: none;
            }}
        </style>

        <audio id="hidden-audio" controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
            """

    st.markdown(
        md,
        unsafe_allow_html=True,
    )

def main():
    st.title("Interview Simulator")

    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = False

    if 'messages' not in st.session_state:
        interview_name = st.text_input('What is your name?')
        interview_position = st.text_input('What role are you applying for?')
        selected_value = st.slider('Choose Interview Difficulty', min_value=0, max_value=10, step=1, value=5)
        if st.button('Start Interview'):
            interview_prompt = f'user want you to act as an interviewer. user will be the candidate and you will ask user the interview questions for the {interview_position} position. My first sentence is "Hi"'
            message_list = [
                {"role": "system", "content": interview_prompt},
                {"role": "user", "content": f"user want you to only reply as the interviewer. Do not write all the conversation at once. user want you to only do the interview with user. Ask user the questions and wait for my answers. Do not write explanations. Ask user the questions one by one like an interviewer does and wait for my answers. Let the difficulty of the questions asked be {selected_value} from a scale of 0 to 10, where 0 means user has just a beginner in the field, and 10 meaning that the user has advance knowledge of the subject. After asking {number_of_questions} questions user want you to let user know whether user got the job or not and how well user scored. You have to tell user whether user got the job or not straight away after the interview. Make sure to tell user my score at the end of the interview out of 10. My name is {interview_name}. Ask user my first question about {interview_position}."}
            ]
            st.session_state['messages'] = message_list
            response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state['messages']
                )
            msg = response.choices[0].message.content
            st.session_state['messages'].append({"role": "assistant", "content": msg})
            st.session_state.interview_state = True
            st.rerun()

    if 'interview_state' in st.session_state and st.session_state.interview_state:
        user_input = st.chat_input('Reply')
        if user_input is not None:
            st.session_state['messages'].append({"role": "user", "content": user_input})
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state['messages']
            )
            msg = response.choices[0].message.content
            st.session_state['messages'].append({"role": "assistant", "content": msg})
        
        messages = st.session_state['messages'][2:]
        print(len(messages))
        for i, message in enumerate (messages):
            if i%2==0:
                writer = st.chat_message('assistant')
                if i == (len(messages)-1):
                    openai_tts(message['content'])
            else:
                writer = st.chat_message('user')
            writer.write(message['content'])

        if len(messages) > number_of_questions+1:
            content = ''
            for i, message in enumerate (messages):
                if i%2==0:
                    content = content + '\n' + 'Question: ' + message['content']
                else:
                    content = content + '\n\n' + 'Response: ' + message['content']
            st.download_button(
                label="Download Conversation",
                data=content,
                file_name='Interview.txt',
                mime='text/plain'
            )


if __name__ == '__main__':
    main()