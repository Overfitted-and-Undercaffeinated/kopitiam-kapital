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
    camera.position.y = 0 // Centered view

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

    // Enhanced lighting for better contours
    const ambientLight = new THREE.AmbientLight(0xFFE4B5, 0.5)
    scene.add(ambientLight)

    const sunLight = new THREE.DirectionalLight(0xFFD4A3, 0.8)
    sunLight.position.set(10, 20, 5)
    sunLight.castShadow = true
    sunLight.shadow.mapSize.width = 2048
    sunLight.shadow.mapSize.height = 2048
    sunLight.shadow.camera.near = 0.5
    sunLight.shadow.camera.far = 50
    scene.add(sunLight)

    const fillLight = new THREE.DirectionalLight(0xE8C4A0, 0.3)
    fillLight.position.set(-10, 10, -5)
    scene.add(fillLight)
    
    // Add rim light for better contours
    const rimLight = new THREE.DirectionalLight(0xFFE8D0, 0.4)
    rimLight.position.set(0, 5, -10)
    scene.add(rimLight)

    // Create Ground Plane with realistic desert texture
    function createGround() {
      const groundGeometry = new THREE.PlaneGeometry(100, 50, 50, 50)
      const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0xD4A574,
        roughness: 0.95,
        metalness: 0,
        flatShading: false,
      })
      const ground = new THREE.Mesh(groundGeometry, groundMaterial)
      ground.rotation.x = -Math.PI / 2
      ground.position.y = -10
      ground.receiveShadow = true
      
      // Add subtle height variation for sand dunes effect
      const positions = ground.geometry.attributes.position
      for (let i = 0; i < positions.count; i++) {
        const x = positions.getX(i)
        const y = positions.getY(i)
        const wave = Math.sin(x * 0.1) * 0.3 + Math.cos(y * 0.15) * 0.2
        positions.setZ(i, wave)
      }
      positions.needsUpdate = true
      ground.geometry.computeVertexNormals()
      
      return ground
    }

    // Add ground to scene
    const ground = createGround()
    scene.add(ground)
    
    // Create realistic mountain ranges with multiple layers for depth
    function createMountainRange() {
      const mountainGroup = new THREE.Group()
      
      // Layer 1: Far distant (lightest, most transparent)
      const farDistant1 = new THREE.Shape()
      farDistant1.moveTo(0, 0)
      farDistant1.bezierCurveTo(4, 1, 7, 4, 10, 6)
      farDistant1.bezierCurveTo(13, 7, 16, 5, 20, 4)
      farDistant1.bezierCurveTo(23, 3, 27, 5, 32, 7)
      farDistant1.bezierCurveTo(35, 8, 38, 6, 42, 4)
      farDistant1.bezierCurveTo(45, 2, 48, 1, 50, 0)
      farDistant1.lineTo(0, 0)
      
      const farDistant1Geo = new THREE.ShapeGeometry(farDistant1)
      const farDistant1Mat = new THREE.MeshStandardMaterial({
        color: 0xA08568,
        transparent: true,
        opacity: 0.35,
        side: THREE.DoubleSide,
        roughness: 1,
      })
      const farDistant1Mesh = new THREE.Mesh(farDistant1Geo, farDistant1Mat)
      farDistant1Mesh.position.set(-25, -10, -30)
      mountainGroup.add(farDistant1Mesh)
      
      // Layer 2: Far distant right side
      const farDistant2 = new THREE.Shape()
      farDistant2.moveTo(0, 0)
      farDistant2.bezierCurveTo(5, 2, 9, 5, 13, 7)
      farDistant2.bezierCurveTo(16, 8, 19, 6, 23, 5)
      farDistant2.bezierCurveTo(26, 4, 30, 6, 35, 8)
      farDistant2.bezierCurveTo(38, 9, 41, 7, 45, 0)
      farDistant2.lineTo(0, 0)
      
      const farDistant2Geo = new THREE.ShapeGeometry(farDistant2)
      const farDistant2Mat = new THREE.MeshStandardMaterial({
        color: 0xA68D75,
        transparent: true,
        opacity: 0.4,
        side: THREE.DoubleSide,
        roughness: 1,
      })
      const farDistant2Mesh = new THREE.Mesh(farDistant2Geo, farDistant2Mat)
      farDistant2Mesh.position.set(10, -10, -28)
      mountainGroup.add(farDistant2Mesh)
      
      // Layer 3: Distant layer
      const distantShape = new THREE.Shape()
      distantShape.moveTo(0, 0)
      distantShape.bezierCurveTo(3, 2, 5, 6, 8, 8)
      distantShape.bezierCurveTo(10, 9, 12, 7, 15, 5)
      distantShape.bezierCurveTo(17, 4, 19, 6, 22, 9)
      distantShape.bezierCurveTo(25, 11, 28, 8, 32, 6)
      distantShape.bezierCurveTo(34, 5, 36, 3, 40, 0)
      distantShape.lineTo(0, 0)
      
      const distantGeometry = new THREE.ShapeGeometry(distantShape)
      const distantMaterial = new THREE.MeshStandardMaterial({
        color: 0xB39174,
        transparent: true,
        opacity: 0.5,
        side: THREE.DoubleSide,
        roughness: 0.9,
      })
      const distantMountain = new THREE.Mesh(distantGeometry, distantMaterial)
      distantMountain.position.set(-20, -10, -22)
      distantMountain.receiveShadow = true
      mountainGroup.add(distantMountain)
      
      // Layer 4: Mid-distant layer left
      const midDistant1 = new THREE.Shape()
      midDistant1.moveTo(0, 0)
      midDistant1.bezierCurveTo(3, 3, 6, 8, 9, 10)
      midDistant1.bezierCurveTo(11, 11, 13, 9, 16, 7)
      midDistant1.bezierCurveTo(19, 6, 22, 8, 26, 11)
      midDistant1.bezierCurveTo(29, 12, 32, 10, 36, 0)
      midDistant1.lineTo(0, 0)
      
      const midDistant1Geo = new THREE.ShapeGeometry(midDistant1)
      const midDistant1Mat = new THREE.MeshStandardMaterial({
        color: 0xBE9D7E,
        transparent: true,
        opacity: 0.6,
        side: THREE.DoubleSide,
        roughness: 0.88,
      })
      const midDistant1Mesh = new THREE.Mesh(midDistant1Geo, midDistant1Mat)
      midDistant1Mesh.position.set(-18, -10, -20)
      midDistant1Mesh.receiveShadow = true
      mountainGroup.add(midDistant1Mesh)
      
      // Layer 5: Mid layer
      const midShape = new THREE.Shape()
      midShape.moveTo(0, 0)
      midShape.bezierCurveTo(2, 3, 4, 7, 7, 10)
      midShape.bezierCurveTo(9, 11, 11, 9, 14, 7)
      midShape.bezierCurveTo(16, 6, 18, 8, 21, 11)
      midShape.bezierCurveTo(23, 12, 25, 10, 28, 7)
      midShape.bezierCurveTo(30, 5, 32, 2, 35, 0)
      midShape.lineTo(0, 0)
      
      const midGeometry = new THREE.ShapeGeometry(midShape)
      const midMaterial = new THREE.MeshStandardMaterial({
        color: 0xC8956E,
        transparent: true,
        opacity: 0.7,
        side: THREE.DoubleSide,
        roughness: 0.85,
      })
      const midMountain = new THREE.Mesh(midGeometry, midMaterial)
      midMountain.position.set(0, -10, -16)
      midMountain.receiveShadow = true
      midMountain.castShadow = true
      mountainGroup.add(midMountain)
      
      // Layer 6: Foreground distant right
      const foreMid1 = new THREE.Shape()
      foreMid1.moveTo(0, 0)
      foreMid1.bezierCurveTo(2, 2, 4, 6, 7, 9)
      foreMid1.bezierCurveTo(9, 10, 11, 8, 14, 6)
      foreMid1.bezierCurveTo(16, 5, 18, 7, 21, 10)
      foreMid1.bezierCurveTo(23, 11, 25, 9, 28, 0)
      foreMid1.lineTo(0, 0)
      
      const foreMid1Geo = new THREE.ShapeGeometry(foreMid1)
      const foreMid1Mat = new THREE.MeshStandardMaterial({
        color: 0xCFA279,
        transparent: true,
        opacity: 0.8,
        side: THREE.DoubleSide,
        roughness: 0.88,
      })
      const foreMid1Mesh = new THREE.Mesh(foreMid1Geo, foreMid1Mat)
      foreMid1Mesh.position.set(15, -10, -14)
      foreMid1Mesh.receiveShadow = true
      foreMid1Mesh.castShadow = true
      mountainGroup.add(foreMid1Mesh)
      
      // Layer 7: Foreground layer (closest)
      const foreShape = new THREE.Shape()
      foreShape.moveTo(0, 0)
      foreShape.bezierCurveTo(2, 2, 4, 5, 6, 8)
      foreShape.bezierCurveTo(8, 10, 10, 11, 13, 9)
      foreShape.bezierCurveTo(15, 8, 17, 9, 19, 12)
      foreShape.bezierCurveTo(21, 14, 23, 13, 26, 10)
      foreShape.bezierCurveTo(28, 8, 30, 4, 32, 0)
      foreShape.lineTo(0, 0)
      
      const foreGeometry = new THREE.ShapeGeometry(foreShape)
      const foreMaterial = new THREE.MeshStandardMaterial({
        color: 0xD4A280,
        transparent: true,
        opacity: 0.85,
        side: THREE.DoubleSide,
        roughness: 0.9,
      })
      const foreMountain = new THREE.Mesh(foreGeometry, foreMaterial)
      foreMountain.position.set(-10, -10, -11)
      foreMountain.receiveShadow = true
      foreMountain.castShadow = true
      mountainGroup.add(foreMountain)
      
      // Layer 8: Far left side mountain
      const farLeft = new THREE.Shape()
      farLeft.moveTo(0, 0)
      farLeft.bezierCurveTo(3, 3, 6, 7, 10, 9)
      farLeft.bezierCurveTo(13, 10, 16, 8, 20, 6)
      farLeft.bezierCurveTo(23, 5, 26, 7, 30, 10)
      farLeft.bezierCurveTo(33, 11, 36, 9, 40, 0)
      farLeft.lineTo(0, 0)
      
      const farLeftGeo = new THREE.ShapeGeometry(farLeft)
      const farLeftMat = new THREE.MeshStandardMaterial({
        color: 0xA68D75,
        transparent: true,
        opacity: 0.45,
        side: THREE.DoubleSide,
        roughness: 1,
      })
      const farLeftMesh = new THREE.Mesh(farLeftGeo, farLeftMat)
      farLeftMesh.position.set(-50, -10, -26)
      mountainGroup.add(farLeftMesh)
      
      // Layer 9: Near left side mountain
      const nearLeft = new THREE.Shape()
      nearLeft.moveTo(0, 0)
      nearLeft.bezierCurveTo(2, 4, 5, 9, 8, 11)
      nearLeft.bezierCurveTo(10, 12, 12, 10, 15, 8)
      nearLeft.bezierCurveTo(17, 7, 19, 9, 22, 12)
      nearLeft.bezierCurveTo(25, 13, 28, 11, 32, 0)
      nearLeft.lineTo(0, 0)
      
      const nearLeftGeo = new THREE.ShapeGeometry(nearLeft)
      const nearLeftMat = new THREE.MeshStandardMaterial({
        color: 0xC8A485,
        transparent: true,
        opacity: 0.75,
        side: THREE.DoubleSide,
        roughness: 0.88,
      })
      const nearLeftMesh = new THREE.Mesh(nearLeftGeo, nearLeftMat)
      nearLeftMesh.position.set(-35, -10, -15)
      nearLeftMesh.receiveShadow = true
      nearLeftMesh.castShadow = true
      mountainGroup.add(nearLeftMesh)
      
      return mountainGroup
    }
    
    // Add mountain range
    const mountains = createMountainRange()
    scene.add(mountains)

    // Create Cowboy Hat
    function createCowboyHat() {
      const hatGroup = new THREE.Group()

      // Hat brim - softer with more segments
      const brimGeometry = new THREE.CylinderGeometry(2.5, 3, 0.3, 64)
      const brimMaterial = new THREE.MeshStandardMaterial({
        color: 0x8B6F47,
        roughness: 0.85,
        metalness: 0.05,
        flatShading: false,
      })
      const brim = new THREE.Mesh(brimGeometry, brimMaterial)
      brim.castShadow = true
      brim.receiveShadow = true
      hatGroup.add(brim)

      // Hat crown base with smoother transitions
      const crownBaseGeometry = new THREE.CylinderGeometry(1.8, 1.9, 0.4, 64)
      const crownBaseMaterial = new THREE.MeshStandardMaterial({
        color: 0xA67C52,
        roughness: 0.8,
        metalness: 0.05,
        flatShading: false,
      })
      const crownBase = new THREE.Mesh(crownBaseGeometry, crownBaseMaterial)
      crownBase.position.y = 0.35
      crownBase.castShadow = true
      crownBase.receiveShadow = true
      hatGroup.add(crownBase)

      // Hat crown - more segments for smoother look
      const crownGeometry = new THREE.CylinderGeometry(1.5, 1.8, 2.5, 64)
      const crownMaterial = new THREE.MeshStandardMaterial({
        color: 0xA67C52,
        roughness: 0.8,
        metalness: 0.05,
        flatShading: false,
      })
      const crown = new THREE.Mesh(crownGeometry, crownMaterial)
      crown.position.y = 1.6
      crown.castShadow = true
      crown.receiveShadow = true
      hatGroup.add(crown)

      // Hat band with better definition
      const bandGeometry = new THREE.CylinderGeometry(1.85, 1.85, 0.35, 64)
      const bandMaterial = new THREE.MeshStandardMaterial({
        color: 0x5C4033,
        roughness: 0.6,
        metalness: 0.2,
        flatShading: false,
      })
      const band = new THREE.Mesh(bandGeometry, bandMaterial)
      band.position.y = 0.65
      band.castShadow = true
      band.receiveShadow = true
      hatGroup.add(band)

      hatGroup.position.y = 2
      return hatGroup
    }

    // Create highly realistic Saguaro cactus
    function createCactus(height: number, hasArms: boolean = true) {
      const cactusGroup = new THREE.Group()
      const cactusColor = 0x6B8E5F // More realistic green

      // Main body - tapered with ridges
      const bodyGeometry = new THREE.CylinderGeometry(0.35, 0.45, height, 12, 16)
      const cactusMaterial = new THREE.MeshStandardMaterial({
        color: cactusColor,
        roughness: 0.92,
        metalness: 0,
        flatShading: false,
      })
      
      // Add vertical ridges to the body
      const positions = bodyGeometry.attributes.position
      for (let i = 0; i < positions.count; i++) {
        const x = positions.getX(i)
        const y = positions.getY(i)
        const z = positions.getZ(i)
        const angle = Math.atan2(z, x)
        const ridge = Math.sin(angle * 6) * 0.04 // 12 ridges
        const distance = Math.sqrt(x * x + z * z)
        const newDistance = distance + ridge
        positions.setX(i, Math.cos(angle) * newDistance)
        positions.setZ(i, Math.sin(angle) * newDistance)
      }
      positions.needsUpdate = true
      bodyGeometry.computeVertexNormals()
      
      const body = new THREE.Mesh(bodyGeometry, cactusMaterial)
      body.castShadow = true
      body.receiveShadow = true
      cactusGroup.add(body)
      
      // Add rounded top cap
      const capGeometry = new THREE.SphereGeometry(0.35, 12, 12, 0, Math.PI * 2, 0, Math.PI / 2)
      const cap = new THREE.Mesh(capGeometry, cactusMaterial)
      cap.position.y = height / 2
      cap.castShadow = true
      cap.receiveShadow = true
      cactusGroup.add(cap)

      if (hasArms) {
        // Left arm - curved and realistic
        const leftArmGeometry = new THREE.CylinderGeometry(0.22, 0.26, height * 0.5, 12, 12)
        const leftArmPositions = leftArmGeometry.attributes.position
        for (let i = 0; i < leftArmPositions.count; i++) {
          const x = leftArmPositions.getX(i)
          const y = leftArmPositions.getY(i)
          const z = leftArmPositions.getZ(i)
          const angle = Math.atan2(z, x)
          const ridge = Math.sin(angle * 6) * 0.03
          const distance = Math.sqrt(x * x + z * z)
          leftArmPositions.setX(i, Math.cos(angle) * (distance + ridge))
          leftArmPositions.setZ(i, Math.sin(angle) * (distance + ridge))
        }
        leftArmPositions.needsUpdate = true
        leftArmGeometry.computeVertexNormals()
        
        const leftArm = new THREE.Mesh(leftArmGeometry, cactusMaterial)
        leftArm.position.set(-0.55, height * 0.2, 0)
        leftArm.rotation.z = Math.PI / 3.5
        leftArm.castShadow = true
        leftArm.receiveShadow = true
        cactusGroup.add(leftArm)
        
        // Left arm cap
        const leftCapGeo = new THREE.SphereGeometry(0.22, 12, 12)
        const leftCap = new THREE.Mesh(leftCapGeo, cactusMaterial)
        const leftArmEndX = -0.55 - Math.sin(Math.PI / 3.5) * (height * 0.25)
        const leftArmEndY = height * 0.2 + Math.cos(Math.PI / 3.5) * (height * 0.25)
        leftCap.position.set(leftArmEndX, leftArmEndY, 0)
        leftCap.castShadow = true
        cactusGroup.add(leftCap)

        // Right arm
        const rightArmGeometry = new THREE.CylinderGeometry(0.22, 0.26, height * 0.45, 12, 12)
        const rightArmPositions = rightArmGeometry.attributes.position
        for (let i = 0; i < rightArmPositions.count; i++) {
          const x = rightArmPositions.getX(i)
          const y = rightArmPositions.getY(i)
          const z = rightArmPositions.getZ(i)
          const angle = Math.atan2(z, x)
          const ridge = Math.sin(angle * 6) * 0.03
          const distance = Math.sqrt(x * x + z * z)
          rightArmPositions.setX(i, Math.cos(angle) * (distance + ridge))
          rightArmPositions.setZ(i, Math.sin(angle) * (distance + ridge))
        }
        rightArmPositions.needsUpdate = true
        rightArmGeometry.computeVertexNormals()
        
        const rightArm = new THREE.Mesh(rightArmGeometry, cactusMaterial)
        rightArm.position.set(0.55, height * 0.25, 0)
        rightArm.rotation.z = -Math.PI / 3.8
        rightArm.castShadow = true
        rightArm.receiveShadow = true
        cactusGroup.add(rightArm)
        
        // Right arm cap
        const rightCapGeo = new THREE.SphereGeometry(0.22, 12, 12)
        const rightCap = new THREE.Mesh(rightCapGeo, cactusMaterial)
        const rightArmEndX = 0.55 + Math.sin(Math.PI / 3.8) * (height * 0.225)
        const rightArmEndY = height * 0.25 + Math.cos(Math.PI / 3.8) * (height * 0.225)
        rightCap.position.set(rightArmEndX, rightArmEndY, 0)
        rightCap.castShadow = true
        cactusGroup.add(rightCap)
      }

      return cactusGroup
    }

    // Create Tumbleweed with more organic, realistic look
    function createTumbleweed(size: number = 1) {
      const tumbleweedGroup = new THREE.Group()
      const stickMaterial = new THREE.MeshStandardMaterial({
        color: 0xB5936B,
        roughness: 0.95,
        metalness: 0,
        flatShading: false,
      })

      // Create random sticks with smoother geometry
      for (let i = 0; i < 40; i++) {
        const stickGeometry = new THREE.CylinderGeometry(
          0.015 + Math.random() * 0.01, 
          0.01 + Math.random() * 0.005, 
          size * (0.6 + Math.random() * 0.3), 
          8
        )
        const stick = new THREE.Mesh(stickGeometry, stickMaterial)
        
        const radius = Math.random() * size * 0.4
        const theta = Math.random() * Math.PI * 2
        const phi = Math.random() * Math.PI
        
        stick.position.set(
          radius * Math.sin(phi) * Math.cos(theta),
          radius * Math.sin(phi) * Math.sin(theta),
          radius * Math.cos(phi)
        )
        stick.rotation.set(
          Math.random() * Math.PI,
          Math.random() * Math.PI,
          Math.random() * Math.PI
        )
        
        stick.castShadow = true
        tumbleweedGroup.add(stick)
      }

      return tumbleweedGroup
    }

    // Create fully opaque clouds
    function createCloud() {
      const cloudGroup = new THREE.Group()
      const cloudMaterial = new THREE.MeshBasicMaterial({
        color: 0xFFFBF5,
        transparent: false,
        opacity: 1,
      })

      // Create organic cloud shapes with more puffs
      const positions = [
        { x: 0, y: 0, z: 0, scale: 1.3 },
        { x: 0.9, y: 0.15, z: 0.1, scale: 1.1 },
        { x: -0.9, y: 0.1, z: -0.1, scale: 1 },
        { x: 0.5, y: 0.35, z: 0, scale: 0.8 },
        { x: -0.4, y: 0.3, z: 0.05, scale: 0.75 },
        { x: 1.5, y: -0.05, z: 0, scale: 0.85 },
        { x: -1.3, y: -0.1, z: 0, scale: 0.9 },
        { x: 0.2, y: -0.2, z: 0.1, scale: 0.95 },
        { x: -0.7, y: -0.15, z: -0.05, scale: 0.85 },
      ]

      positions.forEach(pos => {
        const sphereGeometry = new THREE.SphereGeometry(0.5 * pos.scale, 32, 32)
        const sphere = new THREE.Mesh(sphereGeometry, cloudMaterial)
        sphere.position.set(pos.x, pos.y, pos.z)
        sphere.scale.set(1, 0.8, 0.9) // Slightly flatten for realism
        cloudGroup.add(sphere)
      })

      return cloudGroup
    }

    // Add soft, realistic sun with glow
    const sunGeometry = new THREE.SphereGeometry(3, 64, 64)
    const sunMaterial = new THREE.MeshBasicMaterial({
      color: 0xFFE8C8,
      transparent: true,
      opacity: 0.95,
    })
    const sun = new THREE.Mesh(sunGeometry, sunMaterial)
    sun.position.set(0, 12, -20)
    scene.add(sun)
    
    // Add sun glow
    const glowGeometry = new THREE.SphereGeometry(4, 64, 64)
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0xFFF4E0,
      transparent: true,
      opacity: 0.3,
    })
    const glow = new THREE.Mesh(glowGeometry, glowMaterial)
    glow.position.set(0, 12, -20)
    scene.add(glow)

    // Add main cowboy hat - positioned higher
    const cowboyHat = createCowboyHat()
    cowboyHat.position.set(0, 4, 0)
    scene.add(cowboyHat)

    // Add cacti in the scene - planted in the ground
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
      // Position cacti on the ground, partially buried (20% underground)
      cactus.position.set(pos.x, -10 + (pos.height * 0.4), pos.z)
      scene.add(cactus)
      cacti.push(cactus)
    })

    // Add clouds - positioned higher in the sky
    const clouds: Array<{ mesh: THREE.Group; speed: number }> = []
    for (let i = 0; i < 3; i++) {
      const cloud = createCloud()
      cloud.position.set(
        Math.random() * 40 - 20,
        10 + Math.random() * 4, // Much higher in the sky
        -10 - Math.random() * 5
      )
      cloud.scale.set(2, 2, 2)
      scene.add(cloud)
      clouds.push({ mesh: cloud, speed: 0.01 + Math.random() * 0.01 })
    }

    // Add tumbleweeds - rolling on the ground
    const tumbleweeds: Array<{ mesh: THREE.Group; speed: number; rotSpeed: number }> = []
    for (let i = 0; i < 2; i++) {
      const tumbleweed = createTumbleweed(1.5)
      tumbleweed.position.set(
        -20 - Math.random() * 10,
        -9.2, // Just above ground level
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

      // Smooth cowboy hat rotation following mouse (inverted for correct direction)
      targetRotationY = -mouseX * 0.3 // Inverted
      targetRotationX = -mouseY * 0.2 // Inverted
      
      cowboyHat.rotation.y += (targetRotationY - cowboyHat.rotation.y) * 0.05
      cowboyHat.rotation.x += (targetRotationX - cowboyHat.rotation.x) * 0.05
      cowboyHat.rotation.z = Math.sin(Date.now() * 0.001) * 0.05

      // Animate cacti (slight sway)
      cacti.forEach((cactus, index) => {
        cactus.rotation.z = Math.sin(Date.now() * 0.001 + index) * 0.05
      })

      // Animate clouds - let them go completely off screen before resetting
      clouds.forEach(cloud => {
        cloud.mesh.position.x += cloud.speed
        // Cloud width is about 6 units (scale 2), so wait until completely off screen
        if (cloud.mesh.position.x > 30) {
          cloud.mesh.position.x = -30
        }
      })

      // Animate tumbleweeds - roll left to right with correct rotation direction
      tumbleweeds.forEach(tumbleweed => {
        tumbleweed.mesh.position.x += tumbleweed.speed
        tumbleweed.mesh.rotation.z -= tumbleweed.rotSpeed // Negative rotation for correct rolling direction
        
        // Let tumbleweeds go completely off screen before resetting
        if (tumbleweed.mesh.position.x > 30) {
          tumbleweed.mesh.position.x = -30
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

