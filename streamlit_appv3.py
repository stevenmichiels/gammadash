import streamlit as st
import streamlit.components.v1 as components

#st.set_page_config(layout="wide")
st.header("test html import")

# Function to load HTML file based on dropdown selection
def load_html_file(selected_option):
    if selected_option == 1:
        file_path = "test.html"
    elif selected_option == 2:
        file_path = "test2.html"
    else:
        st.warning("Invalid option selected")
        return None

    with open(file_path, 'r', encoding='utf-8') as html_file:
        source_code = html_file.read()
    
    return source_code

# Streamlit app
def main():
    st.title("HTML File Viewer with Dropdown")

    # Dropdown menu for selecting HTML file
    selected_option = st.selectbox("Select HTML File", [1, 2])

    # Load HTML file based on selection
    source_code = load_html_file(selected_option)


       # Create two plots side by side
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Plot 1")
        components.html(source_code, height=600, width = 800)

    # Plot 2
    with col2:
        st.subheader("Plot 2")
        components.html(source_code, height=600, width = 800)
if __name__ == "__main__":
    main()





