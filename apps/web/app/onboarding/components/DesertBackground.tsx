'use client'

import { useEffect, useRef } from 'react'
import * as THREE from 'three'

export default function DesertBackground() {
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
    camera.position.y = 0

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
      alpha: true, 
      antialias: true 
    })
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    containerRef.current.appendChild(renderer.domElement)

    // Enhanced lighting
    const ambientLight = new THREE.AmbientLight(0xFFE4B5, 0.5)
    scene.add(ambientLight)

    const sunLight = new THREE.DirectionalLight(0xFFD4A3, 0.8)
    sunLight.position.set(10, 20, 5)
    scene.add(sunLight)

    const fillLight = new THREE.DirectionalLight(0xE8C4A0, 0.3)
    fillLight.position.set(-10, 10, -5)
    scene.add(fillLight)
    
    const rimLight = new THREE.DirectionalLight(0xFFE8D0, 0.4)
    rimLight.position.set(0, 5, -10)
    scene.add(rimLight)

    // Create Ground
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
    
    const positions = ground.geometry.attributes.position
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i)
      const y = positions.getY(i)
      const wave = Math.sin(x * 0.1) * 0.3 + Math.cos(y * 0.15) * 0.2
      positions.setZ(i, wave)
    }
    positions.needsUpdate = true
    ground.geometry.computeVertexNormals()
    
    scene.add(ground)

    // Create Mountains
    function createMountain(shape: THREE.Shape, color: number, opacity: number, z: number) {
      const geometry = new THREE.ShapeGeometry(shape)
      const material = new THREE.MeshStandardMaterial({
        color,
        transparent: true,
        opacity,
        side: THREE.DoubleSide,
        roughness: 1,
      })
      const mesh = new THREE.Mesh(geometry, material)
      mesh.position.z = z
      mesh.position.y = -10
      return mesh
    }

    // Far mountains
    const farMountain1 = new THREE.Shape()
    farMountain1.moveTo(0, 0)
    farMountain1.bezierCurveTo(4, 1, 7, 4, 10, 6)
    farMountain1.bezierCurveTo(13, 7, 16, 5, 20, 4)
    farMountain1.bezierCurveTo(23, 3, 27, 5, 32, 7)
    farMountain1.bezierCurveTo(35, 8, 38, 6, 42, 4)
    farMountain1.bezierCurveTo(45, 2, 48, 1, 50, 0)
    farMountain1.lineTo(0, 0)
    const farMountain1Mesh = createMountain(farMountain1, 0xA08568, 0.35, -30)
    farMountain1Mesh.position.x = -25
    scene.add(farMountain1Mesh)

    // Mid mountains
    const midMountain = new THREE.Shape()
    midMountain.moveTo(0, 0)
    midMountain.bezierCurveTo(2, 3, 4, 7, 7, 10)
    midMountain.bezierCurveTo(9, 11, 11, 9, 14, 7)
    midMountain.bezierCurveTo(16, 6, 18, 8, 21, 11)
    midMountain.bezierCurveTo(23, 12, 25, 10, 28, 7)
    midMountain.bezierCurveTo(30, 5, 32, 2, 35, 0)
    midMountain.lineTo(0, 0)
    const midMountainMesh = createMountain(midMountain, 0xC8956E, 0.7, -16)
    scene.add(midMountainMesh)

    // Foreground mountain
    const foreMountain = new THREE.Shape()
    foreMountain.moveTo(0, 0)
    foreMountain.bezierCurveTo(2, 2, 4, 5, 6, 8)
    foreMountain.bezierCurveTo(8, 10, 10, 11, 13, 9)
    foreMountain.bezierCurveTo(15, 8, 17, 9, 19, 12)
    foreMountain.bezierCurveTo(21, 14, 23, 13, 26, 10)
    foreMountain.bezierCurveTo(28, 8, 30, 4, 32, 0)
    foreMountain.lineTo(0, 0)
    const foreMountainMesh = createMountain(foreMountain, 0xD4A280, 0.85, -11)
    foreMountainMesh.position.x = -10
    scene.add(foreMountainMesh)

    // Add sun
    const sunGeometry = new THREE.SphereGeometry(3, 64, 64)
    const sunMaterial = new THREE.MeshBasicMaterial({
      color: 0xFFE8C8,
      transparent: true,
      opacity: 0.95,
    })
    const sun = new THREE.Mesh(sunGeometry, sunMaterial)
    sun.position.set(0, 12, -20)
    scene.add(sun)
    
    // Sun glow
    const glowGeometry = new THREE.SphereGeometry(4, 64, 64)
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0xFFF4E0,
      transparent: true,
      opacity: 0.3,
    })
    const glow = new THREE.Mesh(glowGeometry, glowMaterial)
    glow.position.set(0, 12, -20)
    scene.add(glow)

    // Create clouds
    function createCloud() {
      const cloudGroup = new THREE.Group()
      const cloudMaterial = new THREE.MeshBasicMaterial({
        color: 0xFFFBF5,
        transparent: false,
        opacity: 1,
      })

      const positions = [
        { x: 0, y: 0, z: 0, scale: 1.3 },
        { x: 0.9, y: 0.15, z: 0.1, scale: 1.1 },
        { x: -0.9, y: 0.1, z: -0.1, scale: 1 },
        { x: 0.5, y: 0.35, z: 0, scale: 0.8 },
        { x: -0.4, y: 0.3, z: 0.05, scale: 0.75 },
      ]

      positions.forEach(pos => {
        const sphereGeometry = new THREE.SphereGeometry(0.5 * pos.scale, 32, 32)
        const sphere = new THREE.Mesh(sphereGeometry, cloudMaterial)
        sphere.position.set(pos.x, pos.y, pos.z)
        sphere.scale.set(1, 0.8, 0.9)
        cloudGroup.add(sphere)
      })

      return cloudGroup
    }

    // Add clouds
    const clouds: Array<{ mesh: THREE.Group; speed: number }> = []
    for (let i = 0; i < 3; i++) {
      const cloud = createCloud()
      cloud.position.set(
        Math.random() * 40 - 20,
        10 + Math.random() * 4,
        -10 - Math.random() * 5
      )
      cloud.scale.set(2, 2, 2)
      scene.add(cloud)
      clouds.push({ mesh: cloud, speed: 0.01 + Math.random() * 0.01 })
    }

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate)

      // Animate clouds
      clouds.forEach(cloud => {
        cloud.mesh.position.x += cloud.speed
        if (cloud.mesh.position.x > 25) {
          cloud.mesh.position.x = -25
        }
      })

      renderer.render(scene, camera)
    }

    animate()

    // Handle resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      containerRef.current?.removeChild(renderer.domElement)
      renderer.dispose()
    }
  }, [])

  return <div ref={containerRef} className="fixed inset-0 pointer-events-none z-0" />
}

