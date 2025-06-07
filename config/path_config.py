# # config/path_config.py

# import os

# # For development (local folder)
# UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")

# # For deployment later (network shared folder)
# # UPLOADS_DIR = r"\\HOST_PC_NAME\SharedFolderName"  # uncomment this during deployment

# # Ensure uploads directory exists during development
# if not os.path.exists(UPLOADS_DIR):
#     os.makedirs(UPLOADS_DIR)


# config/path_config.py
import os

UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
