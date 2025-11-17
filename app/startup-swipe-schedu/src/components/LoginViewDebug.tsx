import { useState } from 'react'

export function LoginViewDebug() {
  console.log('LoginView rendering...')
  
  return (
    <div style={{ 
      backgroundColor: 'red', 
      padding: '20px', 
      color: 'white',
      position: 'relative',
      zIndex: 10,
      minHeight: '100vh'
    }}>
      <h1>DEBUG LOGIN VIEW</h1>
      <div style={{ backgroundColor: 'blue', padding: '10px', margin: '10px 0' }}>
        <label style={{ display: 'block', color: 'yellow' }}>Email Label</label>
        <input 
          type="email" 
          placeholder="test@test.com"
          style={{ 
            width: '100%', 
            padding: '10px', 
            fontSize: '16px',
            backgroundColor: 'white',
            color: 'black'
          }} 
        />
      </div>
      <div style={{ backgroundColor: 'green', padding: '10px', margin: '10px 0' }}>
        <label style={{ display: 'block', color: 'yellow' }}>Password Label</label>
        <input 
          type="password" 
          placeholder="password"
          style={{ 
            width: '100%', 
            padding: '10px', 
            fontSize: '16px',
            backgroundColor: 'white',
            color: 'black'
          }} 
        />
      </div>
      <button style={{ padding: '10px 20px', fontSize: '16px' }}>Login</button>
    </div>
  )
}
