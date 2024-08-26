# streamlit-jodit

Streamlit component that allows you to use Jodit HTML editor in streamlit. Jodit is a open source rich text editor
https://xdsoft.net/jodit/

This component is based on react wrapper - https://github.com/jodit/jodit-react 

## Installation instructions

```sh
pip install streamlit-jodit
```

## Usage instructions


```python
import streamlit as st

from streamlit_jodit import st_jodit

config={
            
            'minHeight':300,
        'uploader': {
            'insertImageAsBase64URI': True,
            'imagesExtensions': ['jpg', 'png', 'jpeg', 'gif', 'svg', 'webp']
                    },
             }
content = st_jodit(config)
st.write(content)
```
By default code will pass **readonly:false** to config. 
List of options for config is available at https://xdsoft.net/jodit/docs/options.html
