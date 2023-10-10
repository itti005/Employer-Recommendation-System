from emp.models import Company




def project_one():
    print("Hello World")
    company = Company(
    name="Example Company",
    emp_name="John Doe",
    emp_contact="123-456-7890",
    state_c=1,  # Replace with the actual state ID
    city_c=1,   # Replace with the actual city ID
    address="123 Main St",
    email="example@example.com",
    logo="logo.png",  # Replace with the actual logo file path
    description="This is an example company",

     )


    company.save()
    print("Jagaur")


    
    
    