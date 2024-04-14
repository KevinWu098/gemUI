'use client'
import React from 'react'
import './global.sass'
import Nav from './Nav'
import { TypeAnimation } from 'react-type-animation'
import FadeIn from 'react-fade-in'

function page() {
  return (
    <>
      <Nav />
      {/* hero */}
      <section className="hero">
        <div className="text-contain">
          <h1>Making User Interfaces </h1>
          <div
            style={{
              display: 'flex',
              flexDirection: 'row',
              width: 'fit-content'
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: 'row',
                width: 'fit-content'
              }}
            >
              <img src="./lightning.svg" style={{width: '60px', marginRight:"14px"}} />
              <h1>Actionable</h1>
              <h1 style={{margin:"0 14px"}}>and</h1>
            </div>
            <div
              style={{
                display: 'flex',
                flexDirection: 'row',
                width: 'fit-content'
              }}
            >
              <img src="./flower.svg" style={{width: '60px', marginRight:"18px"}}/>
              <h1>Meaningful</h1>
            </div>
          </div>
          <div className="hero-text">
            with a single input box
        </div>
        </div>
        <div className="input-contain">
          <div className="spark-contain">
            <p>✦</p>
          </div>
          <TypeAnimation
            sequence={[
              'Where is the nearest appointment...',
              1500,
              'Order a pizza for me...',
              1500,
              'How do I get to the nearest gas station...',
              1500
            ]}
            wrapper="span"
            speed={30}
            style={{ fontSize: '2em', textAlign: 'center' }}
            repeat={Infinity}
          />
        </div>
        <button className="hero">✦ Sign up ✦</button>
      </section>
    </>
  )
}

export default page
