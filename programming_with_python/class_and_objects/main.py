from user import User
from post import Post

app_user_one = User("fab@email.com", "fabi", "pwd", "devops eng")
post_by_user1 = Post("How to learn Devops", app_user_one.name)
app_user_one.get_user_info()
post_by_user1.get_post_info()

app_user_one.change_job_title("Data scientist")
app_user_one.get_user_info()

