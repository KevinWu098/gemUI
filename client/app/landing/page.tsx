'use client'
import React from 'react'
import './global.sass'
import Nav from './Nav'
import { TypeAnimation } from 'react-type-animation'
function page() {
  return (
    <>
      <Nav />
      {/* hero */}
      <section className="hero">
        <div className="text-contain">
          <h1>Making User Interfaces </h1>
        </div>
        <div className="input-contain">
          <TypeAnimation
            sequence={[
              // Same substring at the start will only be typed out once, initially
              'We produce food for Mice',
              1000, // wait 1s before replacing "Mice" with "Hamsters"
              'We produce food for Hamsters',
              1000,
              'We produce food for Guinea Pigs',
              1000,
              'We produce food for Chinchillas',
              1000
            ]}
            wrapper="span"
            speed={50}
            style={{ fontSize: '2em', display: 'inline-block' }}
            repeat={Infinity}
          />
        </div>
      </section>
    </>
  )
}

export default page
