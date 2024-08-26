import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
  ComponentProps
} from "streamlit-component-lib"
import React, { ReactNode,useState, useRef, useMemo,useEffect } from "react"
import JoditEditor from "jodit-react"
import ResizeObserver from "resize-observer-polyfill"
import katex from "katex"

//const JoditEditor = dynamic(() => import("jodit-react"), { ssr: false });



interface StreamlitJoditProps extends ComponentProps {
  args: any
}

const StreamlitJodit = ({ args }: StreamlitJoditProps) => {
  const divRef = useRef<HTMLDivElement>(null)
  const editor = useRef(null)
  const  [content, setContent] = useState('')

  let timeout: NodeJS.Timeout

  const config=useMemo(
      () =>(args.config
          ),
      [],
      )

  //const handleChange = () => {
    //clearTimeout(timeout)
    //console.log(content)
    //timeout = setTimeout(() => {
      //Streamlit.setComponentValue(content)//args.html ? content : editor.getText())
    //}, 200)
  //}

  useEffect(() => {
    Streamlit.setFrameHeight()

    window.katex = katex

    const ro = new ResizeObserver(() => {
      Streamlit.setFrameHeight()
    })

    if (divRef.current)
      ro.observe(divRef.current)

    return () => ro.disconnect()
  })

  Streamlit.setComponentValue(content)
  return <div ref={divRef}>
    <JoditEditor
			ref={editor}
			value={content}
			config={config}
            onBlur={newContent => setContent(newContent)}
            onChange={newContent =>{}}

		/>
  </div>

}

export default withStreamlitConnection(StreamlitJodit)