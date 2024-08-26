import os
import streamlit.components.v1 as components


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("streamlit_jodit"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "streamlit_jodit",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_jodit", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def st_jodit(config=None,key='jodit'):
    if config is None:
       config={
           'readonly':False
               }

    component_value= _component_func(config=config,key=key)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
if not _RELEASE:
    import streamlit as st



    # Create an instance of our component with a constant `name` arg, and
    # print its output value.
    #num_clicks = streamlit_summernote()
   # st.markdown("You've clicked %s times!" % int(num_clicks))

    #st.markdown("---")


    # Create a second instance of our component whose `name` arg will vary
    # based on a text_input widget.
    #
    # We use the special "key" argument to assign a fixed identity to this
    # component instance. By default, when a component's arguments change,
    # it is considered a new instance and will be re-mounted on the frontend
    # and lose its current state. In this case, we want to vary the component's
    # "name" argument without having it get recreated.
    #name_input = st.text_input("Enter a name", value="Streamlit")
    config={

            'minHeight':300,
        'uploader': {
            'insertImageAsBase64URI': True,
            'imagesExtensions': ['jpg', 'png', 'jpeg', 'gif', 'svg', 'webp']
                    },
             }
    content = st_jodit()
    st.write(content)


