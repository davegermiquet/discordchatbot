from langchain.prompts import SystemMessagePromptTemplate

with open('systemessage.template', 'r') as file:
    template_content = file.read()
system_message_prompt =  SystemMessagePromptTemplate.from_template(template_content)
system_message = system_message_prompt.format()
