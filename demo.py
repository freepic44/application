import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
from PIL import Image
import requests
import io
import uuid
import os
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state.get("authentication_status"):
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('AI Image Editor 🪄')

    # App Selection using GIFs
    app_options = {
        "Expand Photo": "1.gif",
        "Linkedin Photo": "2.gif",
        "HD Photo Quality": "3.gif",
        "Remove Object": "4.gif",
        "Change Color": "5.gif",
        "Restore Old Photo": "6.gif"
    }

    # Store the selected app in session_state
    if "selected_app" not in st.session_state:
        st.session_state.selected_app = None

    cols = st.columns(3)
    for index, (app_name, gif_path) in enumerate(app_options.items()):
        col = cols[index % 3]
        with col:
            if st.button(f"{app_name}", key=app_name):
                st.session_state.selected_app = app_name
            st.image(gif_path, use_column_width=True)

    if st.session_state.selected_app:
        selected_app = st.session_state.selected_app

        # Function to clear uploaded file from session state
        def clear_uploaded_file():
            if "uploaded_file" in st.session_state:
                del st.session_state["uploaded_file"]

        # App 1: Image Extension
        if selected_app == "Expand Photo":
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

            # Store the uploaded file in session_state
            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file

            # Clear session state if no file is uploaded
            if uploaded_file is None:
                clear_uploaded_file()

            if "uploaded_file" in st.session_state:
                unique_filename = f"temp_image_{uuid.uuid4().hex}.jpg"

                with open(unique_filename, "wb") as f:
                    f.write(st.session_state.uploaded_file.getbuffer())

                st.image(unique_filename, caption="Uploaded Image", use_column_width=True)

                aspect_ratio = st.selectbox(
                    "Select Aspect Ratio",
                    options=["1:1", "4:3", "16:9"],
                    index=0
                )

                gravity = st.selectbox(
                    "Select Gravity",
                    options=["center", "north", "south", "east", "west"],
                    index=0
                )

                size = st.slider("Select Extension Size (in pixels)", 100, 1000, 500)

                if st.button("Extend Image"):
                    public_id = f"genfill-image-{uuid.uuid4().hex}"
                    upload_result = cloudinary.uploader.upload(unique_filename, public_id=public_id)

                    extended_image_url, _ = cloudinary_url(
                        public_id,
                        aspect_ratio=aspect_ratio,
                        gravity=gravity,
                        background="gen_fill",
                        crop="pad",
                        width=size
                    )

                    original_image = Image.open(unique_filename)
                    response = requests.get(extended_image_url)
                    extended_image = Image.open(io.BytesIO(response.content))

                    st.subheader("Compare Images")
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.image(original_image, caption="Original Image", use_column_width=True)

                    with col2:
                        st.image(extended_image, caption="Extended Image", use_column_width=True)

                os.remove(unique_filename)

        # App 2: Replace item in photo
        elif selected_app == "Linkedin Photo":
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file

            # Clear session state if no file is uploaded
            if uploaded_file is None:
                clear_uploaded_file()

            if "uploaded_file" in st.session_state:
                unique_filename = f"temp_image_{uuid.uuid4().hex}.jpg"

                with open(unique_filename, "wb") as f:
                    f.write(st.session_state.uploaded_file.getbuffer())

                st.image(unique_filename, caption="Uploaded Image", use_column_width=True)

                item_to_replace = st.text_input("Cloth to Replace", "T Shirt")
                replace_with = st.text_input("Replace With", "Professional Black Blazer")

                if st.button("Replace Item"):
                    public_id = f"replace-image-{uuid.uuid4().hex}"
                    upload_result = cloudinary.uploader.upload(unique_filename, public_id=public_id)

                    replacement_effect = f"gen_replace:from_{item_to_replace};to_{replace_with}"
                    replaced_image_url, _ = cloudinary_url(
                        public_id,
                        effect=replacement_effect
                    )

                    original_image = Image.open(unique_filename)
                    response = requests.get(replaced_image_url)
                    transformed_image = Image.open(io.BytesIO(response.content))

                    st.subheader("Compare Images")
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.image(original_image, caption="Original Image", use_column_width=True)

                    with col2:
                        st.image(transformed_image, caption="Transformed Image", use_column_width=True)

                os.remove(unique_filename)

        # App 3: HD Photo Quality
        elif selected_app == "HD Photo Quality":
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file

            # Clear session state if no file is uploaded
            if uploaded_file is None:
                clear_uploaded_file()

            if "uploaded_file" in st.session_state:
                unique_filename = f"temp_image_{uuid.uuid4().hex}.jpg"

                with open(unique_filename, "wb") as f:
                    f.write(st.session_state.uploaded_file.getbuffer())

                st.image(unique_filename, caption="Uploaded Image", use_column_width=True)

                scale_factor = st.slider("Select Upscale Factor", 1, 4, 2)

                if st.button("Upscale Image"):
                    public_id = f"upscale-image-{uuid.uuid4().hex}"
                    upload_result = cloudinary.uploader.upload(unique_filename, public_id=public_id)

                    upscaled_image_url, _ = cloudinary_url(
                        public_id,
                        effect=f"upscale:scale_{scale_factor}"
                    )

                    original_image = Image.open(unique_filename)
                    response = requests.get(upscaled_image_url)
                    upscaled_image = Image.open(io.BytesIO(response.content))

                    st.subheader("Compare Images")
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.image(original_image, caption="Original Image", use_column_width=True)

                    with col2:
                        st.image(upscaled_image, caption="Upscaled Image", use_column_width=True)

                os.remove(unique_filename)

        # App 4: Object Removal
        elif selected_app == "Remove Object":
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file

            # Clear session state if no file is uploaded
            if uploaded_file is None:
                clear_uploaded_file()

            if "uploaded_file" in st.session_state:
                unique_filename = f"temp_image_{uuid.uuid4().hex}.jpg"

                with open(unique_filename, "wb") as f:
                    f.write(st.session_state.uploaded_file.getbuffer())

                st.image(unique_filename, caption="Uploaded Image", use_column_width=True)

                item_to_remove = st.text_input("Item to Remove", "bottle")

                if st.button("Remove Item"):
                    public_id = f"me/rm-{uuid.uuid4().hex}"
                    upload_result = cloudinary.uploader.upload(unique_filename, public_id=public_id)

                    removal_effect = f"gen_remove:prompt_{item_to_remove};multiple_true"
                    removed_image_url, _ = cloudinary_url(
                        public_id,
                        effect=removal_effect
                    )

                    original_image = Image.open(unique_filename)
                    response = requests.get(removed_image_url)
                    transformed_image = Image.open(io.BytesIO(response.content))

                    st.subheader("Compare Images")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.image(original_image, caption="Original Image", use_column_width=True)
                    with col2:
                        st.image(transformed_image, caption="Object Removed", use_column_width=True)

                os.remove(unique_filename)

        # App 5: Change Color
        elif selected_app == "Change Color":
            st.title("Image Item Recoloring with Cloudinary's Generative Recolor")

            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file
                image_bytes = uploaded_file.getvalue()
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()

                st.image(image_bytes, caption="Uploaded Image", use_column_width=True)

                item_to_recolor = st.text_input("Item to Recolor", "armchair")
                new_color = st.text_input("New Color (e.g., 'red', 'FF0000')", "FF00FF")

                if st.button("Recolor Item"):
                    try:
                        upload_result = cloudinary.uploader.upload(image_bytes)
                        public_id = upload_result['public_id']

                        recolor_effect = f"gen_recolor:prompt_{item_to_recolor};to-color_{new_color};multiple_true"
                        recolored_image_url, _ = cloudinary_url(
                            f"{public_id}{file_extension}",
                            effect=recolor_effect
                        )

                        response = requests.get(recolored_image_url)

                        if response.status_code == 200:
                            st.subheader("Compare Images")
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.image(image_bytes, caption="Original Image", use_column_width=True)
                            with col2:
                                st.image(response.content, caption="Recolored Image", use_column_width=True)
                        else:
                            st.error(f"Failed to fetch the recolored image. Status code: {response.status_code}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

        # App 6: Restore Old Photo
        elif selected_app == "Restore Old Photo":

            uploaded_file = st.file_uploader("Upload an image to restore", type=["jpg", "jpeg", "png"])

            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file
                image_bytes = uploaded_file.getvalue()
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()

                st.image(image_bytes, caption="Uploaded Image", use_column_width=True)

                # Initialize restored_image_url
                restored_image_url = None

                if st.button("Restore Image"):
                    try:
                        # Upload the image to Cloudinary
                        upload_result = cloudinary.uploader.upload(image_bytes)
                        public_id = upload_result['public_id']

                        # Generate the restoration image URL
                        restore_effect = "gen_restore"
                        restored_image_url, _ = cloudinary_url(
                            f"{public_id}{file_extension}",
                            effect=restore_effect
                        )

                        response = requests.get(restored_image_url)

                        if response.status_code == 200:
                            st.subheader("Compare Images")
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.image(image_bytes, caption="Original Image", use_column_width=True)
                            with col2:
                                st.image(response.content, caption="Restored Image", use_column_width=True)
                        else:
                            st.error(f"Failed to fetch the restored image. Status code: {response.status_code}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

else:
    st.error('Please login to use the app.')

# Creating a new user registration widget
if not st.session_state.get("authentication_status"):
    with st.expander("Register User", expanded=False):  # Set expanded to False
        try:
            (email_of_registered_user,
             username_of_registered_user,
             name_of_registered_user) = authenticator.register_user(pre_authorization=False)
            if email_of_registered_user:
                st.success('User registered successfully')
                # Saving config file after registration
                with open('config.yaml', 'w', encoding='utf-8') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except RegisterError as e:
            st.error(e)
