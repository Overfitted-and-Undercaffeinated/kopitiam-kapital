'use client'

import { useEffect, useRef } from 'react'
import * as THREE from 'three'

interface CowboySceneProps {
  expression: string
  cursorPosition: { x: number; y: number }
}

export default function CowboyScene({ expression, cursorPosition }: CowboySceneProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

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

    // Create Cowboy Model
    const cowboyGroup = new THREE.Group()
    const headGroup = new THREE.Group()

    // Colors
    const skinColor = 0xD2691E
    const hatColor = 0x8B4513
    const hatBrimColor = 0xA0522D
    const shirtColor = 0xCD853F
    const bandanaColor = 0xDC143C
    const eyeColor = 0x2F1810

    // Head - low-poly sphere
    const headGeometry = new THREE.SphereGeometry(0.5, 8, 6)
    const headMaterial = new THREE.MeshStandardMaterial({ 
      color: skinColor, 
      flatShading: true 
    })
    const head = new THREE.Mesh(headGeometry, headMaterial)
    headGroup.add(head)

    // Hat crown
    const hatCrownGeometry = new THREE.CylinderGeometry(0.5, 0.4, 0.3, 8)
    const hatCrownMaterial = new THREE.MeshStandardMaterial({ 
      color: hatColor, 
      flatShading: true 
    })
    const hatCrown = new THREE.Mesh(hatCrownGeometry, hatCrownMaterial)
    hatCrown.position.y = 0.4
    headGroup.add(hatCrown)

    // Hat top
    const hatTopGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.2, 8)
    const hatTop = new THREE.Mesh(hatTopGeometry, hatCrownMaterial)
    hatTop.position.y = 0.6
    headGroup.add(hatTop)

    // Hat brim
    const hatBrimGeometry = new THREE.CylinderGeometry(0.7, 0.7, 0.05, 8)
    const hatBrimMaterial = new THREE.MeshStandardMaterial({ 
      color: hatBrimColor, 
      flatShading: true 
    })
    const hatBrim = new THREE.Mesh(hatBrimGeometry, hatBrimMaterial)
    hatBrim.position.y = 0.5
    headGroup.add(hatBrim)

    // Eyes
    const eyeGeometry = new THREE.SphereGeometry(0.08, 6, 4)
    const eyeMaterial = new THREE.MeshStandardMaterial({ 
      color: eyeColor, 
      flatShading: true 
    })
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
    leftEye.position.set(-0.15, 0.15, 0.4)
    headGroup.add(leftEye)

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
    rightEye.position.set(0.15, 0.15, 0.4)
    headGroup.add(rightEye)

    // Eyebrows
    const eyebrowGeometry = new THREE.BoxGeometry(0.15, 0.03, 0.03)
    const leftEyebrow = new THREE.Mesh(eyebrowGeometry, eyeMaterial)
    leftEyebrow.position.set(-0.15, 0.25, 0.4)
    headGroup.add(leftEyebrow)

    const rightEyebrow = new THREE.Mesh(eyebrowGeometry, eyeMaterial)
    rightEyebrow.position.set(0.15, 0.25, 0.4)
    headGroup.add(rightEyebrow)

    // Mouth
    const mouthGeometry = new THREE.TorusGeometry(0.15, 0.03, 6, 12, Math.PI)
    const mouth = new THREE.Mesh(mouthGeometry, eyeMaterial)
    mouth.position.set(0, -0.1, 0.45)
    headGroup.add(mouth)

    // Nose
    const noseGeometry = new THREE.ConeGeometry(0.06, 0.1, 4)
    const noseMaterial = new THREE.MeshStandardMaterial({ 
      color: hatBrimColor, 
      flatShading: true 
    })
    const nose = new THREE.Mesh(noseGeometry, noseMaterial)
    nose.position.set(0, 0.05, 0.5)
    headGroup.add(nose)

    cowboyGroup.add(headGroup)

    // Body
    const bodyGeometry = new THREE.BoxGeometry(0.6, 0.8, 0.4)
    const bodyMaterial = new THREE.MeshStandardMaterial({ 
      color: shirtColor, 
      flatShading: true 
    })
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
    body.position.y = -0.8
    cowboyGroup.add(body)

    // Arms
    const armGeometry = new THREE.CylinderGeometry(0.08, 0.08, 0.6, 6)
    const armMaterial = new THREE.MeshStandardMaterial({ 
      color: skinColor, 
      flatShading: true 
    })
    
    const leftArm = new THREE.Mesh(armGeometry, armMaterial)
    leftArm.position.set(-0.4, -0.7, 0)
    leftArm.rotation.z = 0.3
    cowboyGroup.add(leftArm)

    const rightArm = new THREE.Mesh(armGeometry, armMaterial)
    rightArm.position.set(0.4, -0.7, 0)
    rightArm.rotation.z = -0.3
    cowboyGroup.add(rightArm)

    // Bandana
    const bandanaGeometry = new THREE.TorusGeometry(0.25, 0.08, 6, 8)
    const bandanaMaterial = new THREE.MeshStandardMaterial({ 
      color: bandanaColor, 
      flatShading: true 
    })
    const bandana = new THREE.Mesh(bandanaGeometry, bandanaMaterial)
    bandana.position.y = -0.4
    cowboyGroup.add(bandana)

    scene.add(cowboyGroup)

    // Animation state
    let mouseX = 0
    let mouseY = 0

    // Update expression
    const updateExpression = () => {
      // Reset to defaults
      leftEye.scale.set(1, 1, 1)
      rightEye.scale.set(1, 1, 1)
      mouth.rotation.x = 0
      mouth.scale.set(1, 1, 1)
      leftEyebrow.rotation.z = 0
      rightEyebrow.rotation.z = 0

      switch (expression) {
        case 'concerned':
          leftEye.scale.set(0.8, 1.2, 1)
          rightEye.scale.set(0.8, 1.2, 1)
          mouth.rotation.x = Math.PI
          mouth.scale.set(0.6, 1, 1)
          leftEyebrow.rotation.z = -0.3
          rightEyebrow.rotation.z = 0.3
          break
        case 'impressed':
          leftEye.scale.set(1.3, 1.3, 1)
          rightEye.scale.set(1.3, 1.3, 1)
          mouth.scale.set(0.4, 1, 1)
          break
        case 'happy':
          leftEye.scale.set(0.7, 0.7, 1)
          rightEye.scale.set(0.7, 0.7, 1)
          mouth.scale.set(0.8, 1, 1)
          break
      }
    }

    // Animation loop
    const clock = new THREE.Clock()
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

      // Eyes following cursor
      const eyeX = mouseX * 0.05
      const eyeY = mouseY * 0.05
      
      leftEye.position.x += (-0.15 + eyeX - leftEye.position.x) * 0.2
      leftEye.position.y += (0.15 + eyeY - leftEye.position.y) * 0.2
      
      rightEye.position.x += (0.15 + eyeX - rightEye.position.x) * 0.2
      rightEye.position.y += (0.15 + eyeY - rightEye.position.y) * 0.2

      // Update expression
      updateExpression()

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
      if (containerRef.current) {
        containerRef.current.removeChild(renderer.domElement)
      }
      renderer.dispose()
    }
  }, [expression, cursorPosition])

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
}
