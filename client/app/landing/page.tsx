'use client'
import React from 'react'
import './global.sass'
import Nav from './Nav'
import { TypeAnimation } from 'react-type-animation'
import FadeIn from 'react-fade-in'
import { Parallax, ParallaxLayer } from '@react-spring/parallax'
import ScrollAnimation from 'react-animate-on-scroll'
function page() {
  return (
    <>
      <Nav />
      <Parallax pages={3} style={{ background: '#f0f0f0' }}>
        {/* hero */}
        <ParallaxLayer
          offset={0}
          speed={1}
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '0px',
            height: '100vh'
          }}
        >
          <section className="hero">
   
            <div className="text-contain">
              <FadeIn delay={2}>
                <h1>Making User Interfaces</h1>
              </FadeIn>

              <div
                style={{
                  display: 'flex',
                  flexDirection: 'row',
                  width: 'fit-content'
                }}
              >
                <FadeIn delay={7}>
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'row',
                      width: 'fit-content'
                    }}
                  >
                    <img
                      src="./lightning.svg"
                      style={{ width: '60px', marginRight: '14px' }}
                    />
                    <h1>Actionable</h1>
                    <h1 style={{ margin: '0 14px' }}>and</h1>
                  </div>
                </FadeIn>
                <FadeIn delay={12}>
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'row',
                      width: 'fit-content'
                    }}
                  >
                    <img
                      src="./flower.svg"
                      style={{ width: '60px', marginRight: '18px' }}
                    />
                    <h1>Meaningful</h1>
                  </div>
                </FadeIn>
              </div>
              <div className="hero-text">with a single input box</div>
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
        </ParallaxLayer>

        {/* parallax */}
        <ParallaxLayer
          offset={1}
          speed={0.5}
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            position: 'relative',
            height: '100vh'
          }}
        >
          <div className="parallax">
            <ScrollAnimation animateIn="fadeIn">
              <div
                className="sticky-img-contain"
                style={{
                  height: '100vh',
                  display: 'flex',
                  flexDirection: 'column',
                  padding: '0 56px',
                  zIndex: 999
                }}
              >
                <img src="./gemui_mockup.svg" alt="" />
              </div>
            </ScrollAnimation>
          </div>
        </ParallaxLayer>
      </Parallax>
    </>
  )
}

export default page
