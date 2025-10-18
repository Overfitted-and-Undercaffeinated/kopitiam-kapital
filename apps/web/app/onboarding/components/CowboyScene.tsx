'use client'

import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'

interface CowboySceneProps {
  expression: string
  cursorPosition: { x: number; y: number }
  onSceneReady?: () => void
}

export default function CowboyScene({ expression, cursorPosition, onSceneReady }: CowboySceneProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isMounted, setIsMounted] = useState(false)
  const sceneReadyRef = useRef(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    if (!isMounted || !containerRef.current) return
    if (typeof window === 'undefined') return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = null

    // Camera
    const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000)
    camera.position.set(0, 0, 3)

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
      alpha: true, 
      antialias: true 
    })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    containerRef.current.appendChild(renderer.domElement)

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8)
    scene.add(ambientLight)

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 1)
    directionalLight1.position.set(5, 5, 5)
    scene.add(directionalLight1)

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5)
    directionalLight2.position.set(-5, 5, -5)
    scene.add(directionalLight2)

    // Create Cowboy Model - Brawl Stars Colt inspired style
    const cowboyGroup = new THREE.Group()
    const headGroup = new THREE.Group()

    // Colors - Brawl Stars inspired palette
    const skinColor = 0xFFB38A      // Warm peachy cartoon skin
    const hairColor = 0x4A3728      // Dark brown hair
    const hatColor = 0xA67C52       // Tan cowboy hat
    const hatBrimColor = 0x8B6F47   // Darker brim
    const hatBandColor = 0x5C4033   // Dark brown band
    const shirtColor = 0x3498DB     // Blue shirt (Colt style)
    const vestColor = 0x8B7355      // Brown vest
    const eyeWhite = 0xFFFFFF
    const eyeColor = 0x2C3E50       // Dark blue eyes
    const eyebrowColor = 0x2F1810

    // HEAD - Cartoon proportions (bigger head)
    const headGeometry = new THREE.SphereGeometry(0.7, 32, 32)
    const headMaterial = new THREE.MeshToonMaterial({ 
      color: skinColor,
      gradientMap: null // Flat toon shading
    })
    const head = new THREE.Mesh(headGeometry, headMaterial)
    head.scale.set(1, 1.05, 0.9) // Slightly taller
    headGroup.add(head)

    // COWBOY HAT - Clean and stylized
    // Hat brim
    const hatBrimGeometry = new THREE.CylinderGeometry(1.1, 1.3, 0.1, 32)
    const hatBrimMaterial = new THREE.MeshToonMaterial({ 
      color: hatBrimColor
    })
    const hatBrim = new THREE.Mesh(hatBrimGeometry, hatBrimMaterial)
    hatBrim.position.y = 0.75
    headGroup.add(hatBrim)

    // Hat crown base
    const hatCrownBaseGeometry = new THREE.CylinderGeometry(0.75, 0.77, 0.2, 32)
    const hatCrownBaseMaterial = new THREE.MeshToonMaterial({ 
      color: hatColor
    })
    const hatCrownBase = new THREE.Mesh(hatCrownBaseGeometry, hatCrownBaseMaterial)
    hatCrownBase.position.y = 0.85
    headGroup.add(hatCrownBase)

    // Hat crown
    const hatCrownGeometry = new THREE.CylinderGeometry(0.6, 0.75, 1.0, 32)
    const hatCrown = new THREE.Mesh(hatCrownGeometry, hatCrownBaseMaterial)
    hatCrown.position.y = 1.4
    headGroup.add(hatCrown)

    // Hat band
    const hatBandGeometry = new THREE.CylinderGeometry(0.77, 0.77, 0.15, 32)
    const hatBandMaterial = new THREE.MeshToonMaterial({
      color: hatBandColor
    })
    const hatBand = new THREE.Mesh(hatBandGeometry, hatBandMaterial)
    hatBand.position.y = 0.95
    headGroup.add(hatBand)

    // EYES - Brawl Stars style (bigger, cartoon eyes)
    // Eye whites
    const eyeWhiteGeometry = new THREE.SphereGeometry(0.15, 16, 16)
    const eyeWhiteMaterial = new THREE.MeshToonMaterial({ 
      color: eyeWhite
    })
    const leftEyeWhite = new THREE.Mesh(eyeWhiteGeometry, eyeWhiteMaterial)
    leftEyeWhite.position.set(-0.25, 0.2, 0.6)
    leftEyeWhite.scale.set(1, 1.1, 0.5)
    headGroup.add(leftEyeWhite)

    const rightEyeWhite = new THREE.Mesh(eyeWhiteGeometry, eyeWhiteMaterial)
    rightEyeWhite.position.set(0.25, 0.2, 0.6)
    rightEyeWhite.scale.set(1, 1.1, 0.5)
    headGroup.add(rightEyeWhite)

    // Pupils
    const pupilGeometry = new THREE.SphereGeometry(0.1, 16, 16)
    const pupilMaterial = new THREE.MeshToonMaterial({ 
      color: eyeColor
    })
    const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
    leftPupil.position.set(-0.25, 0.2, 0.65)
    leftPupil.scale.set(0.8, 0.9, 0.5)
    headGroup.add(leftPupil)

    const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
    rightPupil.position.set(0.25, 0.2, 0.65)
    rightPupil.scale.set(0.8, 0.9, 0.5)
    headGroup.add(rightPupil)

    // Eye highlights (makes them pop)
    const highlightGeometry = new THREE.SphereGeometry(0.05, 8, 8)
    const highlightMaterial = new THREE.MeshBasicMaterial({ 
      color: 0xFFFFFF
    })
    const leftHighlight = new THREE.Mesh(highlightGeometry, highlightMaterial)
    leftHighlight.position.set(-0.22, 0.25, 0.68)
    headGroup.add(leftHighlight)

    const rightHighlight = new THREE.Mesh(highlightGeometry, highlightMaterial)
    rightHighlight.position.set(0.28, 0.25, 0.68)
    headGroup.add(rightHighlight)

    // EYEBROWS - Bold and expressive
    const eyebrowGeometry = new THREE.BoxGeometry(0.2, 0.08, 0.05)
    const eyebrowMaterial = new THREE.MeshToonMaterial({
      color: eyebrowColor
    })
    const leftEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial)
    leftEyebrow.position.set(-0.25, 0.4, 0.6)
    leftEyebrow.rotation.z = -0.2
    headGroup.add(leftEyebrow)

    const rightEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial)
    rightEyebrow.position.set(0.25, 0.4, 0.6)
    rightEyebrow.rotation.z = 0.2
    headGroup.add(rightEyebrow)

    // MOUTH - Simple smile
    const mouthGeometry = new THREE.TorusGeometry(0.18, 0.04, 8, 16, Math.PI)
    const mouthMaterial = new THREE.MeshToonMaterial({
      color: 0x5C3D2E
    })
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
    mouth.position.set(0, -0.05, 0.6)
    mouth.rotation.z = Math.PI
    headGroup.add(mouth)

    // NOSE - Simple stylized
    const noseGeometry = new THREE.SphereGeometry(0.08, 16, 16)
    const noseMaterial = new THREE.MeshToonMaterial({ 
      color: 0xE89B6F // Slightly darker than skin
    })
    const nose = new THREE.Mesh(noseGeometry, noseMaterial)
    nose.position.set(0, 0.1, 0.68)
    nose.scale.set(0.8, 1, 1.2)
    headGroup.add(nose)

    // Hair peeking out from hat
    const hairGeometry = new THREE.SphereGeometry(0.15, 16, 16)
    const hairMaterial = new THREE.MeshToonMaterial({
      color: hairColor
    })
    const leftHair = new THREE.Mesh(hairGeometry, hairMaterial)
    leftHair.position.set(-0.6, 0.5, 0.2)
    leftHair.scale.set(0.6, 1, 0.8)
    headGroup.add(leftHair)

    const rightHair = new THREE.Mesh(hairGeometry, hairMaterial)
    rightHair.position.set(0.6, 0.5, 0.2)
    rightHair.scale.set(0.6, 1, 0.8)
    headGroup.add(rightHair)

    cowboyGroup.add(headGroup)

    // BODY - Smaller than head (cartoon proportions)
    const bodyGeometry = new THREE.BoxGeometry(0.8, 1.0, 0.5)
    const bodyMaterial = new THREE.MeshToonMaterial({ 
      color: shirtColor
    })
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
    body.position.y = -1.2
    cowboyGroup.add(body)

    // VEST - Brown vest over shirt
    const vestGeometry = new THREE.BoxGeometry(0.85, 0.9, 0.52)
    const vestMaterial = new THREE.MeshToonMaterial({ 
      color: vestColor
    })
    const vest = new THREE.Mesh(vestGeometry, vestMaterial)
    vest.position.y = -1.15
    cowboyGroup.add(vest)

    // ARMS - Cartoon style
    const armGeometry = new THREE.CylinderGeometry(0.12, 0.12, 0.7, 16)
    const armMaterial = new THREE.MeshToonMaterial({ 
      color: shirtColor
    })
    
    const leftArm = new THREE.Mesh(armGeometry, armMaterial)
    leftArm.position.set(-0.55, -1.1, 0)
    leftArm.rotation.z = 0.4
    cowboyGroup.add(leftArm)

    const rightArm = new THREE.Mesh(armGeometry, armMaterial)
    rightArm.position.set(0.55, -1.1, 0)
    rightArm.rotation.z = -0.4
    cowboyGroup.add(rightArm)

    // HANDS - Simple rounded hands
    const handGeometry = new THREE.SphereGeometry(0.15, 16, 16)
    const handMaterial = new THREE.MeshToonMaterial({ 
      color: skinColor
    })
    
    const leftHand = new THREE.Mesh(handGeometry, handMaterial)
    leftHand.position.set(-0.75, -1.45, 0)
    leftHand.scale.set(1, 1.2, 0.8)
    cowboyGroup.add(leftHand)

    const rightHand = new THREE.Mesh(handGeometry, handMaterial)
    rightHand.position.set(0.75, -1.45, 0)
    rightHand.scale.set(1, 1.2, 0.8)
    cowboyGroup.add(rightHand)

    // BANDANA - Red neckerchief
    const bandanaGeometry = new THREE.ConeGeometry(0.2, 0.3, 3)
    const bandanaMaterial = new THREE.MeshToonMaterial({ 
      color: 0xE74C3C // Bright red
    })
    const bandana = new THREE.Mesh(bandanaGeometry, bandanaMaterial)
    bandana.position.set(0, -0.6, 0.2)
    bandana.rotation.x = Math.PI
    cowboyGroup.add(bandana)

    // Scale down the entire character to fit container better
    cowboyGroup.scale.set(0.6, 0.6, 0.6)
    
    scene.add(cowboyGroup)

    // Animation state
    let mouseX = 0
    let mouseY = 0

    // Update expression
    const updateExpression = () => {
      // Reset to defaults
      leftEyeWhite.scale.set(1, 1.1, 0.5)
      rightEyeWhite.scale.set(1, 1.1, 0.5)
      leftPupil.position.set(-0.25, 0.2, 0.65)
      rightPupil.position.set(0.25, 0.2, 0.65)
      mouth.rotation.z = Math.PI
      mouth.scale.set(1, 1, 1)
      leftEyebrow.rotation.z = -0.2
      rightEyebrow.rotation.z = 0.2

      switch (expression) {
        case 'concerned':
          // Worried look - eyes wider, eyebrows up
          leftEyeWhite.scale.set(1.2, 1.3, 0.5)
          rightEyeWhite.scale.set(1.2, 1.3, 0.5)
          mouth.rotation.z = 0 // Frown
          mouth.scale.set(0.8, 1, 1)
          leftEyebrow.rotation.z = -0.4
          rightEyebrow.rotation.z = 0.4
          leftEyebrow.position.y = 0.42
          rightEyebrow.position.y = 0.42
          break
        case 'impressed':
          // Excited look - big eyes, big smile
          leftEyeWhite.scale.set(1.3, 1.4, 0.5)
          rightEyeWhite.scale.set(1.3, 1.4, 0.5)
          mouth.scale.set(1.2, 1, 1)
          leftEyebrow.rotation.z = -0.3
          rightEyebrow.rotation.z = 0.3
          break
        case 'happy':
          // Friendly smile - eyes squinted
          leftEyeWhite.scale.set(0.8, 0.9, 0.5)
          rightEyeWhite.scale.set(0.8, 0.9, 0.5)
          mouth.scale.set(1.1, 1, 1)
          leftEyebrow.rotation.z = -0.15
          rightEyebrow.rotation.z = 0.15
          break
      }
      
      // Make sure eyebrow positions reset
      if (expression !== 'concerned') {
        leftEyebrow.position.y = 0.4
        rightEyebrow.position.y = 0.4
      }
    }

    // Animation loop
    const clock = new THREE.Clock()
    let frameCount = 0
    const animate = () => {
      requestAnimationFrame(animate)

      const time = clock.getElapsedTime()

      // Idle floating animation
      cowboyGroup.position.y = Math.sin(time * 1.5) * 0.05

      // Cursor tracking
      mouseX = (cursorPosition.x / window.innerWidth) * 2 - 1
      mouseY = -(cursorPosition.y / window.innerHeight) * 2 + 1

      // Head rotation following cursor
      headGroup.rotation.y += (mouseX * 0.3 - headGroup.rotation.y) * 0.1
      headGroup.rotation.x += (mouseY * 0.2 - headGroup.rotation.x) * 0.1

      // Pupils following cursor (not the whole eye)
      const pupilX = mouseX * 0.06
      const pupilY = mouseY * 0.05
      
      leftPupil.position.x += (-0.25 + pupilX - leftPupil.position.x) * 0.2
      leftPupil.position.y += (0.2 + pupilY - leftPupil.position.y) * 0.2
      
      rightPupil.position.x += (0.25 + pupilX - rightPupil.position.x) * 0.2
      rightPupil.position.y += (0.2 + pupilY - rightPupil.position.y) * 0.2

      // Update expression
      updateExpression()

      renderer.render(scene, camera)
      
      // Notify parent that scene is ready after a few frames
      frameCount++
      if (frameCount === 3 && !sceneReadyRef.current && onSceneReady) {
        sceneReadyRef.current = true
        onSceneReady()
        console.log('🎨 3D Scene fully rendered and ready')
      }
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
      if (containerRef.current) {
        containerRef.current.removeChild(renderer.domElement)
      }
      renderer.dispose()
    }
  }, [expression, cursorPosition])

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
}
