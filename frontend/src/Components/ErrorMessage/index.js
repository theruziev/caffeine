import React from 'react'
import "./index.scss"

export default function ErrorMessage (props) {
  const {title} = props
  const articleClassNames = "message is-small is-danger errorMessage"
  return (<article className={articleClassNames}>
    <div className="message-header">
      <p>{title}</p>
      <button className="delete" aria-label="delete"/>
    </div>
    <div className="message-body">
      <ul className="errorList">
        <li><b>Hello World</b> - Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusantium adipisci alias architecto blanditiis commodi, consequatur corporis debitis deleniti doloribus, excepturi expedita explicabo impedit iste, necessitatibus nihil numquam quidem sequi veniam.</li>
        <li><b>Hello World</b> - Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusantium adipisci alias architecto blanditiis commodi, consequatur corporis debitis deleniti doloribus, excepturi expedita explicabo impedit iste, necessitatibus nihil numquam quidem sequi veniam.</li>
        <li><b>Hello World</b> - Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusantium adipisci alias architecto blanditiis commodi, consequatur corporis debitis deleniti doloribus, excepturi expedita explicabo impedit iste, necessitatibus nihil numquam quidem sequi veniam.</li>
        <li><b>Hello World</b> - Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusantium adipisci alias architecto blanditiis commodi, consequatur corporis debitis deleniti doloribus, excepturi expedita explicabo impedit iste, necessitatibus nihil numquam quidem sequi veniam.</li>

      </ul>
    </div>
  </article>)
}