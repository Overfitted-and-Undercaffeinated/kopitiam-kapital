'use client'

import { useEffect, useRef } from 'react'
import * as THREE from 'three'

interface BacktestCharacterSceneProps {
  isGoodResult: boolean // true = riding bull, false = fighting bear
}

export default function BacktestCharacterScene({ isGoodResult }: BacktestCharacterSceneProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return
    if (typeof window === 'undefined') return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = null

    // Camera
    const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000)
    camera.position.set(0, 0, 8)

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
      alpha: true, 
      antialias: true 
    })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    containerRef.current.appendChild(renderer.domElement)

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7)
    scene.add(ambientLight)

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 1)
    directionalLight1.position.set(5, 5, 5)
    scene.add(directionalLight1)

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5)
    directionalLight2.position.set(-5, 5, -5)
    scene.add(directionalLight2)

    // Main group for the entire scene
    const mainGroup = new THREE.Group()

    // Create Kopikolt character
    const createKopikolt = () => {
      const cowboyGroup = new THREE.Group()
      const headGroup = new THREE.Group()

      // Colors
      const skinColor = 0xFFB38A
      const hairColor = 0x4A3728
      const hatColor = 0xA67C52
      const hatBrimColor = 0x8B6F47
      const hatBandColor = 0x5C4033
      const shirtColor = 0x3498DB
      const vestColor = 0x8B7355
      const eyeWhite = 0xFFFFFF
      const eyeColor = 0x2C3E50
      const eyebrowColor = 0x2F1810

      // HEAD
      const headGeometry = new THREE.SphereGeometry(0.7, 32, 32)
      const headMaterial = new THREE.MeshToonMaterial({ color: skinColor })
      const head = new THREE.Mesh(headGeometry, headMaterial)
      head.scale.set(1, 1.05, 0.9)
      headGroup.add(head)

      // COWBOY HAT
      const hatBrimGeometry = new THREE.CylinderGeometry(1.1, 1.3, 0.1, 32)
      const hatBrimMaterial = new THREE.MeshToonMaterial({ color: hatBrimColor })
      const hatBrim = new THREE.Mesh(hatBrimGeometry, hatBrimMaterial)
      hatBrim.position.y = 0.75
      headGroup.add(hatBrim)

      const hatCrownBaseGeometry = new THREE.CylinderGeometry(0.75, 0.77, 0.2, 32)
      const hatCrownBaseMaterial = new THREE.MeshToonMaterial({ color: hatColor })
      const hatCrownBase = new THREE.Mesh(hatCrownBaseGeometry, hatCrownBaseMaterial)
      hatCrownBase.position.y = 0.85
      headGroup.add(hatCrownBase)

      const hatCrownGeometry = new THREE.CylinderGeometry(0.6, 0.75, 1.0, 32)
      const hatCrown = new THREE.Mesh(hatCrownGeometry, hatCrownBaseMaterial)
      hatCrown.position.y = 1.4
      headGroup.add(hatCrown)

      const hatBandGeometry = new THREE.CylinderGeometry(0.77, 0.77, 0.15, 32)
      const hatBandMaterial = new THREE.MeshToonMaterial({ color: hatBandColor })
      const hatBand = new THREE.Mesh(hatBandGeometry, hatBandMaterial)
      hatBand.position.y = 0.95
      headGroup.add(hatBand)

      // EYES
      const eyeWhiteGeometry = new THREE.SphereGeometry(0.15, 16, 16)
      const eyeWhiteMaterial = new THREE.MeshToonMaterial({ color: eyeWhite })
      
      const leftEyeWhite = new THREE.Mesh(eyeWhiteGeometry, eyeWhiteMaterial)
      leftEyeWhite.position.set(-0.25, 0.2, 0.6)
      leftEyeWhite.scale.set(1.3, 1.4, 0.5) // Excited expression
      headGroup.add(leftEyeWhite)

      const rightEyeWhite = new THREE.Mesh(eyeWhiteGeometry, eyeWhiteMaterial)
      rightEyeWhite.position.set(0.25, 0.2, 0.6)
      rightEyeWhite.scale.set(1.3, 1.4, 0.5)
      headGroup.add(rightEyeWhite)

      // Pupils
      const pupilGeometry = new THREE.SphereGeometry(0.1, 16, 16)
      const pupilMaterial = new THREE.MeshToonMaterial({ color: eyeColor })
      
      const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
      leftPupil.position.set(-0.25, 0.2, 0.65)
      leftPupil.scale.set(0.8, 0.9, 0.5)
      headGroup.add(leftPupil)

      const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
      rightPupil.position.set(0.25, 0.2, 0.65)
      rightPupil.scale.set(0.8, 0.9, 0.5)
      headGroup.add(rightPupil)

      // Eye highlights
      const highlightGeometry = new THREE.SphereGeometry(0.05, 8, 8)
      const highlightMaterial = new THREE.MeshBasicMaterial({ color: 0xFFFFFF })
      
      const leftHighlight = new THREE.Mesh(highlightGeometry, highlightMaterial)
      leftHighlight.position.set(-0.22, 0.25, 0.68)
      headGroup.add(leftHighlight)

      const rightHighlight = new THREE.Mesh(highlightGeometry, highlightMaterial)
      rightHighlight.position.set(0.28, 0.25, 0.68)
      headGroup.add(rightHighlight)

      // EYEBROWS
      const eyebrowGeometry = new THREE.BoxGeometry(0.2, 0.08, 0.05)
      const eyebrowMaterial = new THREE.MeshToonMaterial({ color: eyebrowColor })
      
      const leftEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial)
      leftEyebrow.position.set(-0.25, 0.4, 0.6)
      leftEyebrow.rotation.z = isGoodResult ? -0.3 : -0.5 // Happy or determined
      headGroup.add(leftEyebrow)

      const rightEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial)
      rightEyebrow.position.set(0.25, 0.4, 0.6)
      rightEyebrow.rotation.z = isGoodResult ? 0.3 : 0.5
      headGroup.add(rightEyebrow)

      // MOUTH - Big smile for bull, determined for bear
      const mouthGeometry = new THREE.TorusGeometry(0.18, 0.04, 8, 16, Math.PI)
      const mouthMaterial = new THREE.MeshToonMaterial({ color: 0x5C3D2E })
      const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
      mouth.position.set(0, -0.05, 0.6)
      mouth.rotation.z = Math.PI
      mouth.scale.set(isGoodResult ? 1.2 : 0.9, 1, 1)
      headGroup.add(mouth)

      // NOSE
      const noseGeometry = new THREE.SphereGeometry(0.08, 16, 16)
      const noseMaterial = new THREE.MeshToonMaterial({ color: 0xE89B6F })
      const nose = new THREE.Mesh(noseGeometry, noseMaterial)
      nose.position.set(0, 0.1, 0.68)
      nose.scale.set(0.8, 1, 1.2)
      headGroup.add(nose)

      // Hair
      const hairGeometry = new THREE.SphereGeometry(0.15, 16, 16)
      const hairMaterial = new THREE.MeshToonMaterial({ color: hairColor })
      
      const leftHair = new THREE.Mesh(hairGeometry, hairMaterial)
      leftHair.position.set(-0.6, 0.5, 0.2)
      leftHair.scale.set(0.6, 1, 0.8)
      headGroup.add(leftHair)

      const rightHair = new THREE.Mesh(hairGeometry, hairMaterial)
      rightHair.position.set(0.6, 0.5, 0.2)
      rightHair.scale.set(0.6, 1, 0.8)
      headGroup.add(rightHair)

      cowboyGroup.add(headGroup)

      // BODY
      const bodyGeometry = new THREE.BoxGeometry(0.8, 1.0, 0.5)
      const bodyMaterial = new THREE.MeshToonMaterial({ color: shirtColor })
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
      body.position.y = -1.2
      cowboyGroup.add(body)

      // VEST
      const vestGeometry = new THREE.BoxGeometry(0.85, 0.9, 0.52)
      const vestMaterial = new THREE.MeshToonMaterial({ color: vestColor })
      const vest = new THREE.Mesh(vestGeometry, vestMaterial)
      vest.position.y = -1.15
      cowboyGroup.add(vest)

      // ARMS
      const armGeometry = new THREE.CylinderGeometry(0.12, 0.12, 0.7, 16)
      const armMaterial = new THREE.MeshToonMaterial({ color: shirtColor })
      
      const leftArm = new THREE.Mesh(armGeometry, armMaterial)
      if (isGoodResult) {
        // Riding pose - one arm up celebrating
        leftArm.position.set(-0.55, -0.8, 0)
        leftArm.rotation.z = 0.8
      } else {
        // Fighting pose - arms in fighting position
        leftArm.position.set(-0.55, -1.0, 0.3)
        leftArm.rotation.z = 0.6
      }
      cowboyGroup.add(leftArm)

      const rightArm = new THREE.Mesh(armGeometry, armMaterial)
      if (isGoodResult) {
        // Riding pose - holding reins
        rightArm.position.set(0.55, -1.2, 0)
        rightArm.rotation.z = -0.3
      } else {
        // Fighting pose
        rightArm.position.set(0.55, -1.0, 0.3)
        rightArm.rotation.z = -0.6
      }
      cowboyGroup.add(rightArm)

      // HANDS
      const handGeometry = new THREE.SphereGeometry(0.15, 16, 16)
      const handMaterial = new THREE.MeshToonMaterial({ color: skinColor })
      
      const leftHand = new THREE.Mesh(handGeometry, handMaterial)
      leftHand.position.set(isGoodResult ? -0.75 : -0.75, isGoodResult ? -0.45 : -1.35, isGoodResult ? 0 : 0.3)
      leftHand.scale.set(1, 1.2, 0.8)
      cowboyGroup.add(leftHand)

      const rightHand = new THREE.Mesh(handGeometry, handMaterial)
      rightHand.position.set(isGoodResult ? 0.75 : 0.75, isGoodResult ? -1.5 : -1.35, isGoodResult ? 0 : 0.3)
      rightHand.scale.set(1, 1.2, 0.8)
      cowboyGroup.add(rightHand)

      // BANDANA
      const bandanaGeometry = new THREE.ConeGeometry(0.2, 0.3, 3)
      const bandanaMaterial = new THREE.MeshToonMaterial({ color: 0xE74C3C })
      const bandana = new THREE.Mesh(bandanaGeometry, bandanaMaterial)
      bandana.position.set(0, -0.6, 0.2)
      bandana.rotation.x = Math.PI
      cowboyGroup.add(bandana)

      return cowboyGroup
    }

    // Create BULL (for good results)
    const createBull = () => {
      const bullGroup = new THREE.Group()
      
      // Bull colors
      const bullBodyColor = 0x654321 // Brown
      const bullHornColor = 0xF5F5DC // Beige

      // BODY
      const bodyGeometry = new THREE.BoxGeometry(2, 1.2, 1.5)
      const bodyMaterial = new THREE.MeshToonMaterial({ color: bullBodyColor })
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
      body.position.set(0, -2.5, 0)
      bullGroup.add(body)

      // HEAD
      const headGeometry = new THREE.BoxGeometry(1, 0.8, 0.8)
      const head = new THREE.Mesh(headGeometry, bodyMaterial)
      head.position.set(0, -2.2, 1.3)
      bullGroup.add(head)

      // HORNS
      const hornGeometry = new THREE.ConeGeometry(0.1, 0.6, 8)
      const hornMaterial = new THREE.MeshToonMaterial({ color: bullHornColor })
      
      const leftHorn = new THREE.Mesh(hornGeometry, hornMaterial)
      leftHorn.position.set(-0.4, -1.8, 1.3)
      leftHorn.rotation.z = -0.5
      bullGroup.add(leftHorn)

      const rightHorn = new THREE.Mesh(hornGeometry, hornMaterial)
      rightHorn.position.set(0.4, -1.8, 1.3)
      rightHorn.rotation.z = 0.5
      bullGroup.add(rightHorn)

      // EYES
      const eyeGeometry = new THREE.SphereGeometry(0.08, 16, 16)
      const eyeMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 })
      
      const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
      leftEye.position.set(-0.25, -2.1, 1.7)
      bullGroup.add(leftEye)

      const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
      rightEye.position.set(0.25, -2.1, 1.7)
      bullGroup.add(rightEye)

      // LEGS
      const legGeometry = new THREE.CylinderGeometry(0.15, 0.15, 0.8, 8)
      
      const frontLeftLeg = new THREE.Mesh(legGeometry, bodyMaterial)
      frontLeftLeg.position.set(-0.6, -3.2, 0.6)
      bullGroup.add(frontLeftLeg)

      const frontRightLeg = new THREE.Mesh(legGeometry, bodyMaterial)
      frontRightLeg.position.set(0.6, -3.2, 0.6)
      bullGroup.add(frontRightLeg)

      const backLeftLeg = new THREE.Mesh(legGeometry, bodyMaterial)
      backLeftLeg.position.set(-0.6, -3.2, -0.6)
      bullGroup.add(backLeftLeg)

      const backRightLeg = new THREE.Mesh(legGeometry, bodyMaterial)
      backRightLeg.position.set(0.6, -3.2, -0.6)
      bullGroup.add(backRightLeg)

      // TAIL
      const tailGeometry = new THREE.CylinderGeometry(0.05, 0.08, 0.8, 8)
      const tail = new THREE.Mesh(tailGeometry, bodyMaterial)
      tail.position.set(0, -2.3, -0.8)
      tail.rotation.x = Math.PI / 4
      bullGroup.add(tail)

      return bullGroup
    }

    // Create BEAR (for bad results)
    const createBear = () => {
      const bearGroup = new THREE.Group()
      
      // Bear colors
      const bearBodyColor = 0x5C4033 // Dark brown
      const bearFaceColor = 0x8B7355 // Lighter brown

      // BODY
      const bodyGeometry = new THREE.SphereGeometry(1, 32, 32)
      const bodyMaterial = new THREE.MeshToonMaterial({ color: bearBodyColor })
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
      body.scale.set(1, 1.3, 0.9)
      body.position.set(0, -2.5, 0)
      bearGroup.add(body)

      // HEAD
      const headGeometry = new THREE.SphereGeometry(0.6, 32, 32)
      const head = new THREE.Mesh(headGeometry, bodyMaterial)
      head.position.set(0, -1.2, 0.5)
      bearGroup.add(head)

      // SNOUT
      const snoutGeometry = new THREE.SphereGeometry(0.3, 16, 16)
      const snoutMaterial = new THREE.MeshToonMaterial({ color: bearFaceColor })
      const snout = new THREE.Mesh(snoutGeometry, snoutMaterial)
      snout.position.set(0, -1.3, 1.0)
      snout.scale.set(0.8, 0.7, 1.2)
      bearGroup.add(snout)

      // EARS
      const earGeometry = new THREE.SphereGeometry(0.2, 16, 16)
      
      const leftEar = new THREE.Mesh(earGeometry, bodyMaterial)
      leftEar.position.set(-0.4, -0.8, 0.5)
      bearGroup.add(leftEar)

      const rightEar = new THREE.Mesh(earGeometry, bodyMaterial)
      rightEar.position.set(0.4, -0.8, 0.5)
      bearGroup.add(rightEar)

      // EYES - Angry/fierce
      const eyeGeometry = new THREE.SphereGeometry(0.08, 16, 16)
      const eyeMaterial = new THREE.MeshBasicMaterial({ color: 0xFF0000 }) // Red eyes for fierce
      
      const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
      leftEye.position.set(-0.2, -1.1, 0.85)
      bearGroup.add(leftEye)

      const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
      rightEye.position.set(0.2, -1.1, 0.85)
      bearGroup.add(rightEye)

      // MOUTH - Angry growl
      const mouthGeometry = new THREE.TorusGeometry(0.12, 0.03, 8, 16, Math.PI)
      const mouthMaterial = new THREE.MeshToonMaterial({ color: 0x000000 })
      const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
      mouth.position.set(0, -1.4, 1.05)
      mouth.rotation.z = 0 // Frown
      bearGroup.add(mouth)

      // ARMS - Raised in fighting pose
      const armGeometry = new THREE.CylinderGeometry(0.2, 0.15, 1, 16)
      
      const leftArm = new THREE.Mesh(armGeometry, bodyMaterial)
      leftArm.position.set(-0.9, -1.8, 0.3)
      leftArm.rotation.z = 0.8
      bearGroup.add(leftArm)

      const rightArm = new THREE.Mesh(armGeometry, bodyMaterial)
      rightArm.position.set(0.9, -1.8, 0.3)
      rightArm.rotation.z = -0.8
      bearGroup.add(rightArm)

      // PAWS with claws
      const pawGeometry = new THREE.SphereGeometry(0.2, 16, 16)
      
      const leftPaw = new THREE.Mesh(pawGeometry, bodyMaterial)
      leftPaw.position.set(-1.2, -1.3, 0.4)
      bearGroup.add(leftPaw)

      const rightPaw = new THREE.Mesh(pawGeometry, bodyMaterial)
      rightPaw.position.set(1.2, -1.3, 0.4)
      bearGroup.add(rightPaw)

      // LEGS
      const legGeometry = new THREE.CylinderGeometry(0.25, 0.2, 0.8, 16)
      
      const leftLeg = new THREE.Mesh(legGeometry, bodyMaterial)
      leftLeg.position.set(-0.5, -3.4, 0)
      bearGroup.add(leftLeg)

      const rightLeg = new THREE.Mesh(legGeometry, bodyMaterial)
      rightLeg.position.set(0.5, -3.4, 0)
      bearGroup.add(rightLeg)

      return bearGroup
    }

    // Create the scene based on result
    const kopikolt = createKopikolt()
    kopikolt.scale.set(0.6, 0.6, 0.6)
    
    if (isGoodResult) {
      // Riding the bull
      const bull = createBull()
      kopikolt.position.set(0, 1.5, 0)
      mainGroup.add(bull)
      mainGroup.add(kopikolt)
    } else {
      // Fighting the bear
      const bear = createBear()
      bear.position.set(1.5, 0, 0) // Bear to the right
      kopikolt.position.set(-1, 0, 0.5) // Kopikolt to the left, facing bear
      kopikolt.rotation.y = 0.5 // Turn towards bear
      mainGroup.add(bear)
      mainGroup.add(kopikolt)
    }

    scene.add(mainGroup)

    // Animation
    const clock = new THREE.Clock()
    const animate = () => {
      requestAnimationFrame(animate)
      const time = clock.getElapsedTime()

      if (isGoodResult) {
        // Bull riding motion - bouncing up and down
        mainGroup.position.y = Math.sin(time * 2) * 0.3
        mainGroup.rotation.y = Math.sin(time * 0.5) * 0.1
      } else {
        // Fighting motion - slight sway
        mainGroup.rotation.y = Math.sin(time * 1.5) * 0.05
      }

      renderer.render(scene, camera)
    }

    animate()

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return
      const width = containerRef.current.clientWidth
      const height = containerRef.current.clientHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      if (containerRef.current && renderer.domElement.parentNode === containerRef.current) {
        containerRef.current.removeChild(renderer.domElement)
      }
      renderer.dispose()
    }
  }, [isGoodResult])

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: '100%', 
        height: '100%',
        minHeight: '400px'
      }} 
    />
  )
}

