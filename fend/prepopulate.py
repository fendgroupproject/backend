import random
import string

from models import Author, Project

def populate_with_fake_data():
    url = "https://github.com/fendgroupproject/backend"
    pic_url = "http://www.solplus.co.uk/wp-content/uploads/2013/03/projectManagement.jpg"
    num_of_entries = 6
    for x in range(num_of_entries):
        a = Author(name=''.join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        )
        a.save()
        p = Project(
	    name=''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8)),
	    author_id=a.id,
	    project_version='v1',
	    picture=pic_url,
	    description='some description',
	    link=url
        )
        p.save()
        a.projects.append(p.id)
        a.save()
    
    # Last author will have two projects assigned
    p = Project(
        name=''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8)),
        author_id=a.id,
        project_version='v1',
        picture=pic_url,
        description='some description',
        link=url
    )
    p.save()
    a.projects.append(p.id)
    a.save()
