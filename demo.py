# from GmailAutomation.demo.sendMail import main
from GmailAutomation.RetrivalPipeline.schedular import main

from logger import logger


for email in main():  # keeps looping
    logger.info("📩 New email received in caller: %s", email)
    

# ==================================================================================================================================================

# from GmailAutomation.InsertionPipeline.sendEmail import main
# main()

# ==================================================================================================================================================

# import tempfile, os

# with tempfile.TemporaryDirectory() as tmpdir:
#     print("Created:", tmpdir)
#     file_path = os.path.join(tmpdir, "test.txt")
#     print("File exists initially?", os.path.exists(file_path))
#     with open(file_path, "w") as f:
#         f.write("hello")

#     print("File exists during block?", os.path.exists(file_path))

# print("After block, dir exists?", os.path.exists(tmpdir))
