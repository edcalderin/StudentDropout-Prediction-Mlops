from predictions import get_prediction

import streamlit as st

st.title('Student Dropout classifier')

prediction = ''


def predict():
    # pylint: disable=global-statement
    global prediction

    options = {'Yes': 1, 'No': 0}

    student_features = {
        'student_features': {
            'GDP': gdp,
            'Inflation rate': inflation_rate,
            'Tuition fees up to date': options.get(tuition_fees),
            'Scholarship holder': options.get(scholarship_holder),
            'Curricular units 1st sem (approved)': curr_units_first_sem_approved,
            'Curricular units 1st sem (enrolled)': curr_units_first_sem_enrolled,
            'Curricular units 2nd sem (approved)': curr_units_second_sem_approved,
        },
        'student_id': student_id,
    }
    prediction = get_prediction(student_features)


with st.form('form', clear_on_submit=True):
    student_id = st.text_input(label='Student Id')

    col1, col2 = st.columns(2)
    gdp = col1.number_input(label='GDP', key='gdp')
    inflation_rate = col2.number_input(label='Inflation rate', key='inflation_rate')

    col1, col2 = st.columns(2)
    tuition_fees = col1.selectbox(
        label='Tuition fees up to date', options=['Yes', 'No'], key='tuition_fees'
    )
    scholarship_holder = col2.selectbox(
        label='Scholarship holder', options=['Yes', 'No'], key='scholarship_holder'
    )

    col1, col2, col3 = st.columns(3)
    curr_units_first_sem_approved = col1.number_input(
        label='''Curricular units 1st sem
      \n(approved)
      ''',
        min_value=0,
        help='Number of curricular units approved in the 1st semester',
    )
    curr_units_first_sem_enrolled = col2.number_input(
        label='''Curricular units 1st sem
      \n(enrolled)
      ''',
        min_value=0,
        help='Number of curricular units enrolled in the 1st semester',
    )
    curr_units_second_sem_approved = col3.number_input(
        label='''Curricular units 2nd sem
      \n(approved)
      ''',
        min_value=0,
        help='Number of curricular units approved in the 2nd semester',
    )

    submit_button = st.form_submit_button(label='Predict', use_container_width=True)

    # Markdown to show prediction result
    result_prediction = st.markdown('')

    if submit_button:
        # As soon as the button to be pressed, loading message is printed
        result_prediction.markdown(
            "<h4 style='text-align: center; color: black;'>Loading...</h4>",
            unsafe_allow_html=True,
        )

        predict()

        output = prediction['prediction']['output']

        color = 'green' if output == 'Graduate' else 'red'

        result_prediction.markdown(
            f"""
                    <div style="display: flex; margin: 0 40px;">
                        <div style="flex: 1; display: flex; flex-direction: column;">
                            <label style="font-size: 13px;">Model: {prediction['model']}</label>
                            <label style="font-size: 13px;">Version: {prediction['version']}</label>
                            <label style="font-size: 13px;">Student Id: {prediction['prediction']['student_id']}</label>
                        </div>
                        <div style="flex: 1; display: flex; justify-content: center; align-items: center;">
                            <h2 style='text-align: center; color: {color};'>{output}</h2>
                        </div>
                    </div>""",
            unsafe_allow_html=True,
        )
