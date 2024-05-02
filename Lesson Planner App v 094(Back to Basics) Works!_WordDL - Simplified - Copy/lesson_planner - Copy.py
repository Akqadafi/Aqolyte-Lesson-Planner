import os
from dotenv import load_dotenv
import openai
from worksheet_generator import generate_worksheet_and_fact_sheet

# Load environment variables from the .env file
load_dotenv()

# Fetch API key from the environment variables
API_KEY = os.environ.get('OPENAI_API_KEY')

if API_KEY is None:
    print("API Key not found. Make sure you set the OPENAI_API_KEY environment variable in the .env file.")
else:
    print("API Key: ", API_KEY)

# Set the API key for OpenAI
openai.api_key = API_KEY

def gpt4_request(messages):
    model_name = "gpt-4"
    
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=messages
    )

    if response['choices'][0]['finish_reason'] == 'stop':
        return response['choices'][0]['message']['content']
    else:
        return "Error: The GPT-4 request was not successful"

def parse_lesson_plan(lesson_plan_str):
    sections = lesson_plan_str.split("\n\n")  # Split by blank lines
    lesson_plan_dict = {}
    
    for section in sections:
        if "\nContent: " in section:
            title, content = section.split("\nContent: ")
            title = title.replace("Section: ", "").strip().strip("{}:").strip()
            content = content.strip().strip("{}:").strip().replace("\n", " ")
            lesson_plan_dict[title] = content
        else:
            title = section.replace("Section: ", "").strip().strip("{}:").strip()
            content = ""
            lesson_plan_dict[title] = content

    return lesson_plan_dict

# The lesson plan string (this is just a shortened example for clarity)
lesson_plan_string = """{'Title: Exploring German Geography through the SAMR Model': '', 'Lesson Overview:\nIn this webquest, students will...': ''}"""

# Parse the lesson plan
parsed_lesson_plan = parse_lesson_plan(lesson_plan_string)

# Display the parsed content
for title, content in parsed_lesson_plan.items():
    print(title)
    if content:
        print(content)
    print("\n")

    return lesson_plan_dict

def get_samr_definition():
    with open('samr_definition.txt', 'r') as file:
        samr_definition = file.read()
    return samr_definition

def get_samr_definition():
    return ("The SAMR model, developed by Dr. Ruben Puentedura, offers a method of seeing how computer technology might impact teaching and learning. "
            "It shows a progression that adopters of educational technology often follow as they progress through teaching and learning with technology. "
            "SAMR stands for Substitution, Augmentation, Modification, and Redefinition.")

def integrated_generate_lesson_plan(input_data):
    samr_definition = ""
    if input_data.get('include_samr'):
        samr_definition = get_samr_definition() + "\n\n"
    
    common_statement = (f"The lesson plan should include detailed instructions for the teacher to follow. "
                        f"The lesson plan should be complete and comprehensive, meaning the teacher would need no additional resources in order to use the lesson. "
                        f"Each lesson plan should include a worksheet with facts and details for the students to use. "
                        f"It should be about {input_data['number_of_words']} words, detailed and appropriate for grade {input_data['grade_level']} and a class of {input_data['number_of_students']} students. "
                        f"The cultural makeup of the students includes {', '.join(input_data['culture_group'])}, the Socioeconomic level of the students is {input_data['socioeconomic_level']} with the Experiential Type of {input_data['experiential_type']}. "
                        f"The students include {'Disabled' if input_data['disabled'] else 'Not Disabled'}, {'ELL' if input_data['ell'] else 'Not ELL'}, and {'Gifted' if input_data['gifted'] else 'Not Gifted'}. "
                        f"The lesson should fit the state of {input_data['state']} standards.")
    
   
    return prompt


def generate_lesson_plan(input_data):
    print("Received prompt in generate_lesson_plan:", input_data['prompt'])  # Debug print
    samr_definition = get_samr_definition()
    if input_data['prompt'] == 'prompt0':
        prompt = (f"You are an education specialist tasked with creating a webquest for teachers. "
                  f"The webquest should be based on the SAMR model. The SAMR model is defined as follows:\n\n{samr_definition}\n\n"
                  f"Now, create a webquest lesson that utilizes the SAMR model to teach {input_data['topic']}, that is {input_data['number_of_words']} words to a class of {input_data['grade_level']} grade {input_data['number_of_students']} students. "
                  f"It will also adhere to ISTE standards. "
                  f"The lesson plan should include detailed instructions for the teacher to follow. The lesson plan should be "
                  f"complete and comprehensive, meaning the teacher would need no additional resources in order to use the lesson. "
                  f" Each lesson plan should include a worksheet with facts "
                  f"and details for the students to use. The cultural makeup of the students includes {', '.join(input_data['culture_group'])}, "
                  f"the Socioeconomic level of the students is {input_data['socioeconomic_level']} with the Experiential Type of {input_data['experiential_type']}. The students include {'Disabled' if input_data['disabled'] else 'Not Disabled'}, {'ELL' if input_data['ell'] else 'Not ELL'}, "
                  f"and {'Gifted' if input_data['gifted'] else 'Not Gifted'}. The lesson should fit the state of {input_data['state']} standards.")
    elif input_data['prompt'] == 'prompt1':
    prompt = ("You are an education specialist tasked with creating a {} lesson plan for teachers based on the topic: {}."
              "The lesson plan should begin with a concise overview that provides a snapshot of the lesson's objectives and expected outcomes. "
              "Provide detailed instructions for the teacher, including introductory activities to engage students and concluding remarks or activities to wrap up the lesson. "
              "The lesson plan should be complete and comprehensive, meaning the teacher would need no additional resources to conduct the lesson. "
              "The sections should be organized into title, learning objectives, instructions for the teacher, materials, activities for students, and assessment questions. "
              "Each lesson plan should also come with a worksheet. This worksheet should not only contain facts and details for the students but also visual aids, "
              "like diagrams or images, especially when discussing topics that benefit from visual representation (e.g., planets, biological cells, historical events). "
              "The lesson content should be around {} words, tailored for grade {} and a class size of {} students. "
              "Please consider the cultural backgrounds of the students, which include {}. The socioeconomic level of these students is {}, and their experiential type is {}. "
              "Among these students, some are {}, others are {}, and a few are {}. Ensure the lesson aligns with the {} state standards."
              .format(
                  input_data['lesson_type'],
                  input_data['topic'],
                  input_data['number_of_words'],
                  input_data['grade_level'],
                  input_data['number_of_students'],
                  ', '.join(input_data['culture_group']),
                  input_data['socioeconomic_level'],
                  input_data['experiential_type'],
                  'Disabled' if input_data['disabled'] else 'Not Disabled',
                  'ELL' if input_data['ell'] else 'Not ELL',
                  'Gifted' if input_data['gifted'] else 'Not Gifted',
                  input_data['state']
              ))
    elif input_data['prompt'] == 'prompt2':
    prompt = ("You are an education specialist crafting a concept-based lesson plan for teachers. This lesson "
              "is centered on {}. The plan should be holistic, demanding no additional resources for its execution. "
              "The lesson structure should encompass a title, lesson overview, learning objectives, detailed instructions for the teacher, "
              "necessary materials, and diverse activities for students. The activities should range from discussions to hands-on exercises. "
              "Furthermore, a meticulously detailed worksheet should be integral to the plan. This worksheet should offer specific questions, diagrams, "
              "and content tailored for student engagement. The lesson's blueprint is as follows: "
              "I. Learning Purpose Statement: Pupils will delve deep into {}."
              "II. Input/Instruction: This will encapsulate the essence of {}, from its definition to its attributes, both positive and negative. "
              "Guided practice and informal assessments will further reinforce their grasp on the concept."
              "III. Activity/Independent Practice: Activities that allow students to apply and extend their understanding of {}. "
              "Ensure these activities are interactive and relate the topic to real-world applications. "
              "The lesson, with a word count of approximately {}, should be tailored for a {} grade class comprising {} students. "
              "Considering the class's cultural backdrop of {} and its socioeconomic tier being {}, special attention should be given to the experiential type of {}. "
              "Among these students, there are {}. This lesson should seamlessly align with the educational standards of {}.".format(
                  input_data['topic'],
                  input_data['topic'],
                  input_data['topic'],
                  input_data['topic'],
                  input_data['number_of_words'],
                  input_data['grade_level'],
                  input_data['number_of_students'],
                  ', '.join(input_data['culture_group']),
                  input_data['socioeconomic_level'],
                  input_data['experiential_type'],
                  ', '.join(filter(None, ['Disabled' if input_data['disabled'] else None,
                                          'ELL' if input_data['ell'] else None,
                                          'Gifted' if input_data['gifted'] else None])),
                  input_data['state']
              ))
    elif input_data['prompt'] == 'prompt3':
        prompt = ("You are an education specialist tasked with creating a skills-based lesson plan for teachers. The lesson plan should focus on teaching students a specific skill, and it should be designed to provide detailed instructions for the teacher to follow. The plan should be complete and comprehensive, requiring no additional resources for the teacher to use the lesson in their class. The instructions should be divided into title, instructions for the teacher, materials, activities for students, and assessment questions. Additionally, each lesson plan should include a worksheet with facts and details for the students to use. The topic of the lesson is {}."The lesson plan should include the following:
                  "I. Lesson Plan Purpose Statement:"
                  "What you want students to learn or be able to do."
                  "II. Input:"
                  "Exactly what students need to know in order to perform the skill."
                  "Includes the following: a. Identification of procedural components - Introduce the skill and the specific steps. b. Direct instruction and modeling - Tell how/why the skill is used. Model the use of the skill."
                  "The lesson should be about {} words, detailed, and appropriate for grade {} and a class of {} students. The cultural makeup of the students includes {}. The Socioeconomic level of the students is {} with an {}Experiential  level. The students include {}. The lesson should align with {} standards.".format(
                      input_data['topic'],
                      input_data['number_of_words'],
                      input_data['grade_level'],
                      input_data['number_of_students'],
                      ', '.join(input_data['culture_group']),
                      input_data['socioeconomic_level'],
                      input_data['experiential_type'],
                      'Disabled' if input_data['disabled'] else 'Not Disabled',
                      'ELL' if input_data['ell'] else 'Not ELL',
                      'Gifted' if input_data['gifted'] else 'Not Gifted',
                      input_data['state']
                  ))
    elif input_data['prompt'] == 'prompt4':
        prompt = ("You are an education specialist tasked with creating a reading lesson plan for teachers in the scaffolded reading experience (SRE)  program. The lesson plan should focus on promoting reading enjoyment and comprehension. It should provide detailed instructions for the teacher to follow and be a self-contained plan, requiring no additional resources. The instructions should be organized into sections, including title, teacher instructions, materials, activities for students, and assessment questions. Each lesson plan should also include a worksheet containing facts and details for the students to use during SRE." The lesson should include the following components:
                  "I. Purpose Statement:"
                  "The purpose statement should clearly define the objectives of the lesson for both narrative and expository texts. For narrative texts, the objective is to have students read and enjoy a specific story or chapter. For expository texts, the objective is to have students read and understand a particular book or chapter."
                  "II. Pre-Reading Activity:"
                  "The pre-reading activity should be brief, lasting between 1 to 4 minutes, and designed to prepare students for their reading session."
                  "III. During-Reading:"
                  "Students will engage in independent reading or follow a substitute-friendly reading method during SRE. "
                  "IV. Post-Reading Activity:"
                  "Create an activity that encourages students to interact with ideas from the story they read. For narrative texts, consider including aesthetic response activities that allow students to express their emotional or creative responses to the story."
                  "The lesson should be about {} words, detailed, and appropriate for grade {} and a class of {} students. The cultural makeup of the students includes {}. The Socioeconomic level of the students is {} with an {} Experiential  level. The students include {}. The lesson should align with {} standards.".format(
                      input_data['topic'],
                      input_data['number_of_words'],
                      input_data['grade_level'],
                      input_data['number_of_students'],
                      ', '.join(input_data['culture_group']),
                      input_data['socioeconomic_level'],
                      input_data['experiential_type'],
                      'Disabled' if input_data['disabled'] else 'Not Disabled',
                      'ELL' if input_data['ell'] else 'Not ELL',
                      'Gifted' if input_data['gifted'] else 'Not Gifted',
                      input_data['state']
                  ))
    elif input_data['prompt'] == 'prompt5':
        prompt = ("You are an education specialist tasked with creating a discovery-based lesson plan for teachers. The goal of this lesson plan is to implement discovery learning in a planned and directed manner to teach specific concepts, lessons, or information. The plan should provide detailed instructions for the teacher to follow and be self-contained, requiring no additional resources. It should be organized into sections, including title, teacher instructions, materials, activities for students, and assessment questions. Additionally, each lesson plan should include a worksheet containing relevant facts and details for the students to utilize during the discovery process."The lesson should include the following components:
                  "I. Purpose Statement:"
                  "Clearly define the specific concepts, lessons, or information you want students to learn through discovery. This statement should guide the entire lesson plan."
                  "II. Discovery Activity:"
                  "Identify the elements or key concepts you want students to discover during the lesson. Design an engaging activity that allows students to explore and uncover these elements on their own. After the activity, encourage students to identify or describe the salient elements they discovered."
                  "III. Input:"
                  "Provide students with specific information that directly relates to the lesson's purpose. Use this input to complement their discoveries or to extend their initial findings."
                  "IV. Activity:"
                  "Design an activity that allows students to manipulate, reinforce, or extend their learning based on the elements they discovered. This activity should build upon their explorations and encourage a deeper understanding of the concepts."
                  "The lesson should be about {} words, detailed, and appropriate for grade {} and a class of {} students. The cultural makeup of the students includes {}. The Socioeconomic level of the students is {} with an {} Experiential  level. The students include {}. The lesson should align with {} standards.".format(
                      input_data['topic'],
                      input_data['number_of_words'],
                      input_data['grade_level'],
                      input_data['number_of_students'],
                      ', '.join(input_data['culture_group']),
                      input_data['socioeconomic_level'],
                      input_data['experiential_type'],
                      'Disabled' if input_data['disabled'] else 'Not Disabled',
                      'ELL' if input_data['ell'] else 'Not ELL',
                      'Gifted' if input_data['gifted'] else 'Not Gifted',
                      input_data['state']
                  ))
    else:
        raise ValueError(f'Invalid prompt selected: {input_data["prompt"]}')

    # Create the messages for the GPT model
    messages = [
        {
            "role": "system",
            "content": prompt
        },
    ]
    
    # Call the GPT model and get the generated lesson plan
    lesson_plan_str = gpt4_request(messages)

    # Parse the lesson plan string into a dictionary
    lesson_plan_dict = parse_lesson_plan(lesson_plan_str)

    return lesson_plan_dict


