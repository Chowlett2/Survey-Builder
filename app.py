import streamlit as st
import pandas as pd
import shutil
import os.path
import os
from openai import OpenAI
import openai
import re

################### Main and API Key Credentials #####################
 
# Function to check if the OpenAI API key is valid
def check_api_key(api_key, group, purpose, num_questions):

    gpt_model = "gpt-4o-mini"
    OpenAI_api_key = api_key
    # client= OpenAI(api_key=OpenAI_api_key)
    openai.api_key = OpenAI_api_key

    try:
        q_type_text = 'open'
        response = openai.chat.completions.create(
            model=gpt_model,  
            messages=[
                {"role": "developer", "content": "You are a helpful assistant that generates survey questions for clients of the education analytics company InnovateK12. You will be given a description of the survey target group and "\
                f"the purpose of the survey, and you will generate {num_questions} relevant and insightful survey questions for the specified target group and survey purpose. "\
                f"Your response should be in the format of a numbered list of {num_questions} survey questions. Do not include any text in your response other than the numbered list of survey questions.\n"\
                f"The client will also choose what type of questions they want in their survey. The client has chosen the following question type(s): {q_type_text}"\
                "Only generate questions of these type(s). If the client has selected more than one type of question, make sure there is at least one of each question type in your response."},

                {"role": "user", "content": f"Generate {num_questions} survey questions using the following information. \n"\
                f"Description of target group: {group}\n"\
                f"Purpose of survey: {purpose}"},
            ]
        )
        return True
    
    except:
        return False

# Prompt user for OpenAI API key
api_key = st.text_input("Enter your OpenAI API key", type="password")

# Check if the API key is valid
if api_key:
    if check_api_key(api_key=api_key, group='Parents', purpose='Exam prep curriculum.', num_questions=1):
        st.success("API Key is valid! You can now use the app.")
    else:
        st.error("Invalid API key. Please check your key and try again.")
else:
    st.warning("Please enter a valid OpenAI API key to continue.")

################### GPT Model and API Key ############################

#GPT model
gpt_model = "gpt-4o-mini"
OpenAI_api_key = api_key
# client= OpenAI(api_key=OpenAI_api_key)
openai.api_key = OpenAI_api_key

#################### Helper Functions for LLM Queries #################

def split_into_list(text):
    # Use regex to find text following each numbered bullet (1. to 5.)
    matches = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\Z)', text, re.DOTALL)
    # Strip whitespace and newlines from each item
    return [match.strip() for match in matches]

def choose_questions(survey_questions, selected_numbers=None, chosen_questions=None, rejected_questions=None):
    if selected_numbers is None:
        selected_numbers = []
    if chosen_questions is None:
        chosen_questions = []
    if rejected_questions is None:
        rejected_questions = []

    questions_list = survey_questions.splitlines()
    for line in questions_list:
        parts = line.split('.', 1)
        if len(parts) > 1:
            number = parts[0].strip()
            question = parts[1].strip() 
            try:
                number = int(number)
                if number in selected_numbers:
                    chosen_questions.append(question)
                else:
                    rejected_questions.append(question)
            except ValueError:
                rejected_questions.append(question)
        else:
            continue

    print("Chosen Questions:")
    for question in chosen_questions:
        print(question)
    print("\nRejected Questions:")
    for question in rejected_questions:
        print(question)

    return chosen_questions, rejected_questions

def generate_q_type_text(questions_type):
    if len(questions_type) == 1:
        string1 =  questions_type[0]
    if len(questions_type) == 2:
        string1 =  " and ".join(questions_type)
    if len(questions_type) == 3:
        string1 = ", ".join(questions_type[:-1]) + ", and " + questions_type[-1]

    likert_text = "Likert questions use the likert scale as a means of response. When generating these questions, first state the question, then follow the question with '(Strongly Agree to Strongly Disagree)'."
    open_text = "Open questions are open text response. These questions should be designed to be open-ended and give the responder the ability to answer in as much detail as they desire. These questions should be followed with (Open Response)."
    select_text = "Select questions are select-all-that-apply or multiple choice questions. There should be between 3-8 possible responses. These questions should be followed with the possible responses in parentheses. Do not include any other text besides the possible choices in parentheses, such as 'select all that apply'. The possible answers should not resemble a likert scale. Do not create select questions with answers like (Very Satisfied, Satisfied, Neutral, Unsatisfied, Very Unsatisfied) or (Very Important, Important, Neutral, Not Important, Not Important at All) or similar scales of positive to negative sentiment. Each possible answer should be categorical and distinct. The possible answers should not be a scale of negative to positive sentiment! Other and None can be possible answers for this question type, but do not ask for the client to specify further if other."
    string2=""
    if 'likert' in questions_type:
        string2 += likert_text + "\n"
    if 'open' in questions_type:
        string2 += open_text + "\n"
    if 'select' in questions_type:
        string2 += select_text + "\n"
    return string1 + '.\n' + string2


def new_survey(group, purpose, num_questions, questions_type = ('likert','open','select')):
    q_type_text = generate_q_type_text(questions_type)
    response = openai.chat.completions.create(
        model=gpt_model,  
        messages=[
            {"role": "developer", "content": "You are a helpful assistant that generates survey questions for clients of the education analytics company InnovateK12. You will be given a description of the survey target group and "\
            f"the purpose of the survey, and you will generate {num_questions} relevant and insightful survey questions for the specified target group and survey purpose. "\
            f"Your response should be in the format of a numbered list of {num_questions} survey questions. Do not include any text in your response other than the numbered list of survey questions.\n"\
            f"The client will also choose what type of questions they want in their survey. The client has chosen the following question type(s): {q_type_text}"\
            "Only generate questions of these type(s). If the client has selected more than one type of question, make sure there is at least one of each question type in your response."},

            {"role": "user", "content": f"Generate {num_questions} survey questions using the following information. \n"\
            f"Description of target group: {group}\n"\
            f"Purpose of survey: {purpose}"},
        ]
    )
    return response.choices[0].message.content

def continue_survey(group, purpose, num_questions, chosen_questions, rejected_questions, questions_type = ('likert','open','select')):
    q_type_text = generate_q_type_text(questions_type)
    response = openai.chat.completions.create(
        model=gpt_model,  
        messages=[
            {"role": "developer", "content": "You are a helpful assistant that generates survey questions for clients of the education analytics company InnovateK12. You will be given a description of the survey target group and "\
            f"the purpose of the survey, and you will generate {num_questions} relevant and insightful survey questions for the specified target group and survey purpose. You will also be given a list of previously chosen and rejected survey questions. "\
            "Do not repeat any questions from either list. Use the chosen questions to help generate new questions, and the rejected list to avoid similar questions. Do not simply reword chosen questions, instead ask related but distinct questions. "\
            f"Your response should be in the format of a numbered list of {num_questions} survey questions. "\
            "Do not include any text in your response other than the numbered list of survey questions. "\
            f"The client will also choose what type of questions they want in their survey. The client has chosen the following question type(s): {q_type_text}"\
            "Only generate questions of these type(s). If the client has selected more than one type of question, make sure there is at least one of each question type in your response."},


            {"role": "user", "content": f"Generate {num_questions} survey questions using the following information. \n"\
            f"Description of target group: {group}\n"\
            f"Purpose of survey: {purpose}\n"\
            f"Previously chosen survey questions:\n{chosen_questions}\n"\
            f"Previously rejected survey questions:\n{rejected_questions}"},
        ]
    )
    return response.choices[0].message.content

def restart_survey(group, purpose, num_questions, previous_survey, reason, questions_type = ('likert','open','select')):
    q_type_text = generate_q_type_text(questions_type)
    response = openai.chat.completions.create(
        model=gpt_model,  
        messages=[
            {"role": "developer", "content": "You are a helpful assistant that generates survey questions for clients of the education analytics company InnovateK12. You will be given a description of the survey target group and "\
            f"the purpose of the survey, and you will generate {num_questions} survey questions that best accomplish these goals. The client has already started making a survey through InnovateK12's survey builder, but wishes to start over. "\
            "You will be given the previously chosen survey questions, and the reason for starting over. Use this information to generate new survey questions to meet the client's needs. "\
            f"Your response should be in the format of a numbered list of {num_questions} survey questions. "\
            "Do not include any text in your response other than the numbered list of survey questions." \
            f"The client will also choose what type of questions they want in their survey. The client has chosen the following question type(s): {q_type_text}"\
            "Only generate questions of these type(s). If the client has selected more than one type of question, make sure there is at least one of each question type in your response."},

            {"role": "user", "content": f"Generate {num_questions} survey questions using the following information. \n"\
            f"Description of target group: {group}\n"\
            f"Purpose of survey: {purpose}\n"\
            f"Previously chosen survey questions: {previous_survey}\n"\
            f"Reason for starting over: {reason}"},
        ]
    )
    return response.choices[0].message.content

############# Create/refresh data upload directory #################

# create/refresh data upload directory
data_dir = 'uploaded_data'
if os.path.exists(data_dir):
    shutil.rmtree(data_dir)
os.mkdir('uploaded_data')

st.title(f'Upload Data')

data_frames = []

uploaded_files = st.file_uploader(label='You may upload any CSV or excel files to use as a starting point for the survey. (optional)',
                                  accept_multiple_files=True,
                                  type={'xlsx', 'csv'})

print('Uploaded Files:\n')                             
print(uploaded_files)

if uploaded_files:
    for file in uploaded_files:
        file.seek(0)
    data_frames = [pd.read_csv(file) for file in uploaded_files]
    file_names = [file.name for file in uploaded_files]
    for n, df in enumerate(data_frames):
        df.to_csv(f'uploaded_data/{file_names[n]}')


if len(data_frames) == 1:
    file_count_txt = f':blue[***You have uploaded***] :orange[{len(data_frames)}] :blue[***file.***]'
else:
    file_count_txt = f':blue[***You have uploaded***] :orange[{len(data_frames)}] :blue[***files.***]'

st.write(file_count_txt)

if 'df' in locals():
    st.title(f'Data Viewer')

    for n, df in enumerate(data_frames):
        st.write(f"CSV {n+1}: {uploaded_files[n].name}")
        st.dataframe(data = df)

    dfs = []

    for filename in os.listdir(data_dir):
        f = os.path.join(data_dir, filename)
        if os.path.isfile(f) and f.endswith('.csv'):
            df = pd.read_csv(f'uploaded_data/{filename}')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            dfs.append(df)
            print(f'{f} successfully read')
        else:
            print(f'{f} is not an accepted file type')


    if dfs != list():
        for df in dfs:
            print(df.columns)

        if len(dfs) > 1:
            df = dfs[0].append([d for d in dfs[1:]])

        else:
            df = dfs[0]

else:
    df = pd.DataFrame()

st.title(f'Event Details')

############## LLM QUERIES #################################
# Ensure all session state variables are initialized
if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0

if "generated_questions" not in st.session_state:
    st.session_state.generated_questions = []

if "good_questions" not in st.session_state:
    st.session_state.good_questions = []

if "bad_questions" not in st.session_state:
    st.session_state.bad_questions = []

if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = []
if 'good_questions' not in st.session_state:
    st.session_state.good_questions = []
if 'bad_questions' not in st.session_state:
    st.session_state.bad_questions = []
if 'last_group' not in st.session_state:
    st.session_state.last_group = ""
if 'last_purpose' not in st.session_state:
    st.session_state.last_purpose = ""

group_selection = st.text_input("What is the targeted group for this survey?",
                                'Parents, teachers, administrators, and community members.')

purpose_selection = st.text_input("What is the purpose of this event?")

# User input
# Number of survey questions to be generated per round
num_questions = 5

#Open Text Response
group = group_selection
purpose = purpose_selection

print(f'group: {group}')
print(f'purpose: {purpose}')

good_questions = []
bad_questions = []

def multi_select_all(options_list, label="Select Options"):
    def render():
        return st.multiselect(label, options_list, default=options_list)
    return render

q_type_dict = {'Open Response': 'open',
               'Likert Scale': 'likert',
               'Select All': 'select'}

options = q_type_dict.keys()

selectbox = multi_select_all(options, "Select acceptable question types for your survey (you may change at any time).")
selected_q_types = selectbox()  # The selectbox is displayed here

# response #1
if purpose_selection and group_selection:
    if (group_selection != st.session_state.last_group) or (purpose_selection != st.session_state.last_purpose):
        # Reset stored questions as the topic has changed
        st.session_state.good_questions = []
        st.session_state.bad_questions = []

        # Update last inputs
        st.session_state.last_group = group_selection
        st.session_state.last_purpose = purpose_selection
        
        # Query OpenAI API and store result
        survey_questions = new_survey(group_selection, purpose_selection, num_questions, questions_type=tuple([q_type_dict[q_type] for q_type in selected_q_types]))
        st.session_state.generated_questions = split_into_list(survey_questions)

st.title(f'Generated Questions')

if st.session_state.good_questions:
    st.write("Select Desirable Generated Questions:")

for i in st.session_state.generated_questions:
    key = f"{i}_{st.session_state.refresh_key}"  # Unique key for fresh checkboxes
    agree = st.checkbox(f'{i}', key=key)

    if agree:
        if i not in st.session_state.good_questions:
            st.session_state.good_questions.append(i)
        if i in st.session_state.bad_questions:
            st.session_state.bad_questions.remove(i)
    else:
        if i not in st.session_state.bad_questions:
            st.session_state.bad_questions.append(i)
        if i in st.session_state.good_questions:
            st.session_state.good_questions.remove(i)


if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0  # Initialize refresh trigger

if st.button("Generate More Questions"):
    # Clear all stored checkbox states to force re-render
    for question in st.session_state.generated_questions:
        key = f"{question}_{st.session_state.refresh_key}"
        if key in st.session_state:
            del st.session_state[key]

    # Generate a new batch of questions
    new_questions = continue_survey(
        group=st.session_state.last_group, 
        purpose=st.session_state.last_purpose, 
        num_questions=5, 
        chosen_questions=st.session_state.good_questions, 
        rejected_questions=st.session_state.bad_questions,
        questions_type=tuple([q_type_dict[q_type] for q_type in selected_q_types])
    )

    # Store new questions
    st.session_state.generated_questions = split_into_list(new_questions)

    # Increment refresh key to ensure new unique checkbox keys
    st.session_state.refresh_key += 1

    # Force Streamlit to immediately update UI
    st.rerun()

# Show Good Questions
if st.session_state.good_questions:
    st.title("❌ Edit Survey")
    # st.write(st.session_state.good_questions)
    options = st.session_state.good_questions
    selectbox = multi_select_all(options, "Delete any unwanted questions from your final survey:")
    selected = selectbox()  # The selectbox is displayed here
    st.write("The below list contains all questions included in your survey export:", selected)
    added_cols = selected
else:
    st.write("No questions selected yet.")

# Show Bad Questions
if st.session_state.bad_questions:
    # st.write("### ❌ Bad Questions")
    # st.write(st.session_state.bad_questions)
    print('Rejected Questions:')
    print(st.session_state.bad_questions)
# else:
#     st.write("No questions rejected yet.")


############### NAME & DOWNLOAD FILE #######################

download_dir = 'data_files'
if os.path.exists(download_dir):
    shutil.rmtree(download_dir)

os.mkdir('data_files')

if st.session_state.good_questions:
    print(added_cols)
    print(type(added_cols))
    for i in added_cols:
        df[i] = []

    # st.write(f"CSV export viewer")
    # st.dataframe(data = df)

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')


    csv = convert_df(df)
    st.title(f'✅ Finalize Survey')

    # Name file (Optional)
    file_name = st.text_input("Name your downloaded data file (Optional)",
                            'survey')

    # Download ZIP folder
    try:
        st.download_button('Download CSV',
                        csv,
                        f'{file_name}.csv',
                        'text/csv',
                        key='download-csv')
    except:
        st.write(f'Invalid file name. Please rename file.')
        st.download_button('Download CSV',
                    csv,
                    f'{file_name}.csv',
                    'text/csv',
                    key='download-csv')
