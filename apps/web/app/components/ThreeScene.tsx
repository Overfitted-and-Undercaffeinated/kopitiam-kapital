'use client'

import { useEffect, useRef } from 'react'
import * as THREE from 'three'

export default function ThreeScene() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = null
    scene.fog = new THREE.Fog(0xF4A460, 10, 50)

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    )
    camera.position.z = 15
    camera.position.y = 2

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
      alpha: true, 
      antialias: true 
    })
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    containerRef.current.appendChild(renderer.domElement)

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xFFE4B5, 0.6)
    scene.add(ambientLight)

    const sunLight = new THREE.DirectionalLight(0xFFA500, 1)
    sunLight.position.set(10, 20, 5)
    sunLight.castShadow = true
    sunLight.shadow.mapSize.width = 2048
    sunLight.shadow.mapSize.height = 2048
    scene.add(sunLight)

    const fillLight = new THREE.DirectionalLight(0xCD853F, 0.4)
    fillLight.position.set(-10, 10, -5)
    scene.add(fillLight)

    // Create Cowboy Hat
    function createCowboyHat() {
      const hatGroup = new THREE.Group()

      // Hat brim
      const brimGeometry = new THREE.CylinderGeometry(2.5, 3, 0.2, 32)
      const brimMaterial = new THREE.MeshStandardMaterial({
        color: 0x8B4513,
        roughness: 0.8,
        metalness: 0.2,
      })
      const brim = new THREE.Mesh(brimGeometry, brimMaterial)
      brim.castShadow = true
      brim.receiveShadow = true
      hatGroup.add(brim)

      // Hat crown base
      const crownBaseGeometry = new THREE.CylinderGeometry(1.8, 1.8, 0.3, 32)
      const crownBaseMaterial = new THREE.MeshStandardMaterial({
        color: 0xA0522D,
        roughness: 0.7,
        metalness: 0.2,
      })
      const crownBase = new THREE.Mesh(crownBaseGeometry, crownBaseMaterial)
      crownBase.position.y = 0.25
      crownBase.castShadow = true
      hatGroup.add(crownBase)

      // Hat crown
      const crownGeometry = new THREE.CylinderGeometry(1.5, 1.8, 2.5, 32)
      const crownMaterial = new THREE.MeshStandardMaterial({
        color: 0xA0522D,
        roughness: 0.7,
        metalness: 0.2,
      })
      const crown = new THREE.Mesh(crownGeometry, crownMaterial)
      crown.position.y = 1.5
      crown.castShadow = true
      hatGroup.add(crown)

      // Hat band
      const bandGeometry = new THREE.CylinderGeometry(1.85, 1.85, 0.3, 32)
      const bandMaterial = new THREE.MeshStandardMaterial({
        color: 0x2F1810,
        roughness: 0.5,
        metalness: 0.6,
      })
      const band = new THREE.Mesh(bandGeometry, bandMaterial)
      band.position.y = 0.5
      band.castShadow = true
      hatGroup.add(band)

      hatGroup.position.y = 2
      return hatGroup
    }

    // Create Cactus
    function createCactus(height: number, hasArms: boolean = true) {
      const cactusGroup = new THREE.Group()
      const cactusColor = 0x6B8E23

      // Main body
      const bodyGeometry = new THREE.CylinderGeometry(0.4, 0.5, height, 8)
      const cactusMaterial = new THREE.MeshStandardMaterial({
        color: cactusColor,
        roughness: 0.9,
        metalness: 0.1,
      })
      const body = new THREE.Mesh(bodyGeometry, cactusMaterial)
      body.castShadow = true
      body.receiveShadow = true
      cactusGroup.add(body)

      if (hasArms) {
        // Left arm
        const armGeometry = new THREE.CylinderGeometry(0.25, 0.3, height * 0.4, 8)
        const leftArm = new THREE.Mesh(armGeometry, cactusMaterial)
        leftArm.position.set(-0.6, height * 0.15, 0)
        leftArm.rotation.z = Math.PI / 3
        leftArm.castShadow = true
        cactusGroup.add(leftArm)

        // Right arm
        const rightArm = new THREE.Mesh(armGeometry, cactusMaterial)
        rightArm.position.set(0.6, height * 0.2, 0)
        rightArm.rotation.z = -Math.PI / 3
        rightArm.castShadow = true
        cactusGroup.add(rightArm)
      }

      return cactusGroup
    }

    // Create Tumbleweed
    function createTumbleweed(size: number = 1) {
      const tumbleweedGroup = new THREE.Group()
      const stickMaterial = new THREE.MeshStandardMaterial({
        color: 0x8B7355,
        roughness: 0.9,
      })

      // Create random sticks for tumbleweed appearance
      for (let i = 0; i < 30; i++) {
        const stickGeometry = new THREE.CylinderGeometry(0.02, 0.02, size * 0.8, 4)
        const stick = new THREE.Mesh(stickGeometry, stickMaterial)
        
        stick.position.set(
          (Math.random() - 0.5) * size * 0.3,
          (Math.random() - 0.5) * size * 0.3,
          (Math.random() - 0.5) * size * 0.3
        )
        stick.rotation.set(
          Math.random() * Math.PI,
          Math.random() * Math.PI,
          Math.random() * Math.PI
        )
        
        tumbleweedGroup.add(stick)
      }

      return tumbleweedGroup
    }

    // Create Cloud
    function createCloud() {
      const cloudGroup = new THREE.Group()
      const cloudMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFFFFF,
        roughness: 1,
        transparent: true,
        opacity: 0.7,
      })

      // Create fluffy cloud with spheres
      const positions = [
        { x: 0, y: 0, z: 0, scale: 1.2 },
        { x: 1, y: 0.2, z: 0, scale: 1 },
        { x: -1, y: 0.1, z: 0, scale: 0.9 },
        { x: 0.5, y: 0.5, z: 0, scale: 0.8 },
        { x: -0.5, y: 0.4, z: 0, scale: 0.7 },
      ]

      positions.forEach(pos => {
        const sphereGeometry = new THREE.SphereGeometry(0.5 * pos.scale, 16, 16)
        const sphere = new THREE.Mesh(sphereGeometry, cloudMaterial)
        sphere.position.set(pos.x, pos.y, pos.z)
        cloudGroup.add(sphere)
      })

      return cloudGroup
    }

    // Add main cowboy hat
    const cowboyHat = createCowboyHat()
    cowboyHat.position.set(0, 0, 0)
    scene.add(cowboyHat)

    // Add cacti in the scene
    const cacti: THREE.Group[] = []
    const cactusPositions = [
      { x: -8, z: -5, height: 3, hasArms: true },
      { x: -10, z: -3, height: 2.5, hasArms: false },
      { x: 8, z: -4, height: 3.5, hasArms: true },
      { x: 10, z: -6, height: 2, hasArms: false },
      { x: -6, z: -8, height: 2.8, hasArms: true },
    ]

    cactusPositions.forEach(pos => {
      const cactus = createCactus(pos.height, pos.hasArms)
      cactus.position.set(pos.x, pos.height / 2 - 2, pos.z)
      scene.add(cactus)
      cacti.push(cactus)
    })

    // Add clouds
    const clouds: Array<{ mesh: THREE.Group; speed: number }> = []
    for (let i = 0; i < 3; i++) {
      const cloud = createCloud()
      cloud.position.set(
        Math.random() * 40 - 20,
        5 + Math.random() * 3,
        -10 - Math.random() * 5
      )
      cloud.scale.set(2, 2, 2)
      scene.add(cloud)
      clouds.push({ mesh: cloud, speed: 0.01 + Math.random() * 0.01 })
    }

    // Add tumbleweeds
    const tumbleweeds: Array<{ mesh: THREE.Group; speed: number; rotSpeed: number }> = []
    for (let i = 0; i < 2; i++) {
      const tumbleweed = createTumbleweed(1.5)
      tumbleweed.position.set(
        -20 - Math.random() * 10,
        0.5,
        -2 - Math.random() * 3
      )
      scene.add(tumbleweed)
      tumbleweeds.push({
        mesh: tumbleweed,
        speed: 0.03 + Math.random() * 0.02,
        rotSpeed: 0.05 + Math.random() * 0.05,
      })
    }

    // Mouse tracking for cowboy hat
    let mouseX = 0
    let mouseY = 0
    let targetRotationX = 0
    let targetRotationY = 0

    const handleMouseMove = (event: MouseEvent) => {
      mouseX = (event.clientX / window.innerWidth) * 2 - 1
      mouseY = -(event.clientY / window.innerHeight) * 2 + 1
    }

    window.addEventListener('mousemove', handleMouseMove)

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate)

      // Smooth cowboy hat rotation following mouse
      targetRotationY = mouseX * 0.3
      targetRotationX = mouseY * 0.2
      
      cowboyHat.rotation.y += (targetRotationY - cowboyHat.rotation.y) * 0.05
      cowboyHat.rotation.x += (targetRotationX - cowboyHat.rotation.x) * 0.05
      cowboyHat.rotation.z = Math.sin(Date.now() * 0.001) * 0.05

      // Animate cacti (slight sway)
      cacti.forEach((cactus, index) => {
        cactus.rotation.z = Math.sin(Date.now() * 0.001 + index) * 0.05
      })

      // Animate clouds
      clouds.forEach(cloud => {
        cloud.mesh.position.x += cloud.speed
        if (cloud.mesh.position.x > 25) {
          cloud.mesh.position.x = -25
        }
      })

      // Animate tumbleweeds
      tumbleweeds.forEach(tumbleweed => {
        tumbleweed.mesh.position.x += tumbleweed.speed
        tumbleweed.mesh.rotation.z += tumbleweed.rotSpeed
        tumbleweed.mesh.rotation.x += tumbleweed.rotSpeed * 0.5
        
        if (tumbleweed.mesh.position.x > 25) {
          tumbleweed.mesh.position.x = -25
          tumbleweed.mesh.position.z = -2 - Math.random() * 3
        }
      })

      renderer.render(scene, camera)
    }

    animate()

    // Handle window resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('resize', handleResize)
      containerRef.current?.removeChild(renderer.domElement)
      renderer.dispose()
    }
  }, [])

  return <div ref={containerRef} className="absolute inset-0 pointer-events-none" />
}

