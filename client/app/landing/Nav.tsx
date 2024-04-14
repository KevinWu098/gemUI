//* this is a horizontal nav
function Nav() {
  return (
    <div className="grid-row nav-contain">
        <img src="./gemui_small_logo.svg" style={{width: '180px'}}/>
      <nav>
        <ul>
          <li className="grid-row">
            <a href="/" target="_blank" rel="noopener noreferrer">
              Home
            </a>
            <a href="" target="_blank" rel="noopener noreferrer">
              About us
            </a>
            <a href="" target="_blank" rel="noopener noreferrer">
              Product
            </a>
          </li>
          
        </ul>
            
     
      </nav>
      <div className="flex-row" style={{ gap: '12px' }}>
              {/* Sign up  */}
              <button className="primary">Sign up</button>
              {/* Log in */}
              <button className="secondary">Log in </button>
            </div>
    </div>
  )
}

export default Nav
