'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import { EthicalBanner } from '@/components/EthicalBanner';
import {
  Box,
  Sparkles,
  Shield,
  Search,
  Eye,
  RotateCcw,
  Compass,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Archive,
  Volume2,
  VolumeX,
} from 'lucide-react';

import {
  MemoryRoomResponse,
  RoomObject,
  RoomTheme,
  AvatarConfig,
  AvatarSpeechResponse,
} from '@/types';

import { MemoryRoomScene } from '@/components/memory-room/MemoryRoomScene';
import { MemoryRoomControls } from '@/components/memory-room/MemoryRoomControls';
import { MemoryObjectDetails } from '@/components/memory-room/MemoryObjectDetails';
import { MemoryEvidencePanel } from '@/components/memory-room/MemoryEvidencePanel';
import { AvatarSettingsPanel } from '@/components/memory-room/AvatarSettingsPanel';
import { AccessibleMemoryList } from '@/components/memory-room/AccessibleMemoryList';
import { MemoryTimelinePanel } from '@/components/memory-room/MemoryTimelinePanel';
import { MemoryRoomLoadingState } from '@/components/memory-room/MemoryRoomLoadingState';
import { MemoryRoomErrorState } from '@/components/memory-room/MemoryRoomErrorState';

export default function MemoryRoomPage() {
  // --- Data & Loading State ---
  const [roomData, setRoomData] = useState<MemoryRoomResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // --- Filtering & Selection ---
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedObject, setSelectedObject] = useState<RoomObject | null>(null);
  const [hoveredObject, setHoveredObject] = useState<RoomObject | null>(null);

  // --- View Mode & Accessibility ---
  const [is3DView, setIs3DView] = useState<boolean>(true);
  const [webglSupported, setWebglSupported] = useState<boolean>(true);
  const [reducedMotion, setReducedMotion] = useState<boolean>(false);
  const [audioEnabled, setAudioEnabled] = useState<boolean>(true);

  // --- Room Configuration & Avatar ---
  const [theme, setTheme] = useState<RoomTheme>('ARCHIVAL_WARM');
  const [ambientLight, setAmbientLight] = useState<number>(0.8);
  const [avatarConfig, setAvatarConfig] = useState<AvatarConfig | null>(null);
  const [isAvatarSpeaking, setIsAvatarSpeaking] = useState<boolean>(false);

  // --- Modals ---
  const [showEvidenceModal, setShowEvidenceModal] = useState<boolean>(false);
  const [showAvatarSettingsModal, setShowAvatarSettingsModal] = useState<boolean>(false);

  // --- Three.js Refs ---
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<MemoryRoomScene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);

  // Orbit parameters
  const orbitState = useRef({
    theta: 0.0, // horizontal rotation angle
    phi: 0.22, // vertical pitch angle (radians)
    radius: 7.2, // camera distance from center
    targetTheta: 0.0,
    targetPhi: 0.22,
    targetRadius: 7.2,
    center: new THREE.Vector3(0, 1.2, 0),
  });

  const pointerState = useRef({
    isDown: false,
    startX: 0,
    startY: 0,
    prevX: 0,
    prevY: 0,
    dragDistance: 0,
  });

  // Keep speaking and motion states in sync with animation loop
  const isSpeakingRef = useRef<boolean>(false);
  isSpeakingRef.current = isAvatarSpeaking;
  const reducedMotionRef = useRef<boolean>(false);
  reducedMotionRef.current = reducedMotion;

  // --- 1. Check WebGL Capability ---
  const checkWebGL = useCallback((): boolean => {
    try {
      const canvas = document.createElement('canvas');
      const supported = !!(
        window.WebGLRenderingContext &&
        (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
      );
      setWebglSupported(supported);
      if (!supported) {
        setIs3DView(false);
      }
      return supported;
    } catch {
      setWebglSupported(false);
      setIs3DView(false);
      return false;
    }
  }, []);

  // --- 2. Fetch Room Data from Backend ---
  const fetchRoomData = useCallback(
    async (cat: string = selectedCategory, search: string = searchQuery) => {
      setLoading(true);
      setError(null);
      const startTime = performance.now();

      try {
        const params = new URLSearchParams({
          profile_id: 'default-profile-001',
          user_id: 'demo-user-001',
        });
        if (cat && cat !== 'ALL') {
          params.append('category', cat);
        }
        if (search && search.trim()) {
          params.append('search', search.trim());
        }

        const res = await fetch(`/api/v1/memory-room?${params.toString()}`);
        if (!res.ok) {
          throw new Error(`Failed to load memory room (HTTP ${res.status})`);
        }
        const data: MemoryRoomResponse = await res.json();
        setRoomData(data);

        if (data.room_config) {
          setTheme(data.room_config.theme);
          setAmbientLight(data.room_config.ambient_light_intensity);
          setReducedMotion(data.room_config.reduced_motion);
          setAudioEnabled(data.room_config.audio_enabled);
        }

        if (data.avatar) {
          setAvatarConfig(data.avatar);
        }

        // If Three.js scene is active, populate objects immediately
        if (sceneRef.current) {
          sceneRef.current.setObjects(data.objects);
        }

        // Send telemetry metrics
        const initTime = performance.now() - startTime;
        fetch('/api/v1/memory-room/metrics', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            init_time_ms: Math.round(initTime * 10) / 10,
            visible_objects_count: data.objects.length,
            webgl_available: webglSupported,
            fallback_mode_active: !is3DView,
            avatar_loaded: !!data.avatar?.enabled,
            asset_failures: 0,
          }),
        }).catch(() => null);
      } catch (err: any) {
        console.error('Error loading memory room:', err);
        setError(err.message || 'Unable to retrieve 3D memory room records.');
      } finally {
        setLoading(false);
      }
    },
    [selectedCategory, searchQuery, webglSupported, is3DView]
  );

  useEffect(() => {
    checkWebGL();
    fetchRoomData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- 3. Handle Category & Search Changes ---
  const handleCategoryChange = (cat: string) => {
    setSelectedCategory(cat);
    fetchRoomData(cat, searchQuery);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRoomData(selectedCategory, searchQuery);
  };

  // --- 4. Camera Reset Handler ---
  const handleResetCamera = useCallback(() => {
    orbitState.current.targetTheta = 0.0;
    orbitState.current.targetPhi = 0.22;
    orbitState.current.targetRadius = 7.2;
    orbitState.current.center.set(0, 1.2, 0);
  }, []);

  // --- 5. Three.js Scene Setup & Lifecycle ---
  useEffect(() => {
    if (!is3DView || !webglSupported || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 550;

    // Renderer
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: false,
        powerPreference: 'high-performance',
      });
    } catch (e) {
      console.warn('WebGL initialization failed, falling back to accessible list view.', e);
      setWebglSupported(false);
      setIs3DView(false);
      return;
    }

    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Clean container before attaching
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Camera
    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 100);
    cameraRef.current = camera;

    // Scene
    const scene = new MemoryRoomScene(
      theme,
      ambientLight,
      avatarConfig || undefined
    );
    sceneRef.current = scene;

    if (roomData?.objects) {
      scene.setObjects(roomData.objects);
    }

    // Callbacks from scene interactions
    scene.setCallbacks(
      (obj) => {
        setSelectedObject(obj);
      },
      (obj) => {
        setHoveredObject(obj);
      }
    );

    // Initial camera position update
    const initTheta = orbitState.current.theta;
    const initPhi = orbitState.current.phi;
    const initRad = orbitState.current.radius;
    camera.position.set(
      initRad * Math.sin(initTheta) * Math.cos(initPhi),
      orbitState.current.center.y + initRad * Math.sin(initPhi),
      initRad * Math.cos(initTheta) * Math.cos(initPhi)
    );
    camera.lookAt(orbitState.current.center);

    // Resize Observer
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width: w, height: h } = entry.contentRect;
        if (w > 0 && h > 0) {
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
          renderer.setSize(w, h);
        }
      }
    });
    resizeObserver.observe(container);

    // --- Pointer / Orbit Event Listeners ---
    const getNormalizedCoords = (e: PointerEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      return { x, y };
    };

    const handlePointerDown = (e: PointerEvent) => {
      pointerState.current.isDown = true;
      pointerState.current.startX = e.clientX;
      pointerState.current.startY = e.clientY;
      pointerState.current.prevX = e.clientX;
      pointerState.current.prevY = e.clientY;
      pointerState.current.dragDistance = 0;
      renderer.domElement.setPointerCapture(e.pointerId);
    };

    const handlePointerMove = (e: PointerEvent) => {
      const { x, y } = getNormalizedCoords(e);

      if (pointerState.current.isDown) {
        const dx = e.clientX - pointerState.current.prevX;
        const dy = e.clientY - pointerState.current.prevY;
        pointerState.current.prevX = e.clientX;
        pointerState.current.prevY = e.clientY;
        pointerState.current.dragDistance += Math.abs(dx) + Math.abs(dy);

        // Orbit rotation
        orbitState.current.targetTheta -= dx * 0.006;
        orbitState.current.targetPhi = Math.max(
          -0.1,
          Math.min(1.2, orbitState.current.targetPhi + dy * 0.006)
        );
      } else {
        // Raycast hover
        scene.handlePointerMove(x, y, camera);
      }
    };

    const handlePointerUp = (e: PointerEvent) => {
      const wasClick = pointerState.current.dragDistance < 6;
      pointerState.current.isDown = false;
      try {
        renderer.domElement.releasePointerCapture(e.pointerId);
      } catch {}

      if (wasClick) {
        const { x, y } = getNormalizedCoords(e);
        scene.handlePointerClick(x, y, camera);
      }
    };

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomFactor = e.deltaY * 0.005;
      orbitState.current.targetRadius = Math.max(
        2.5,
        Math.min(13.0, orbitState.current.targetRadius + zoomFactor)
      );
    };

    const domElement = renderer.domElement;
    domElement.addEventListener('pointerdown', handlePointerDown);
    domElement.addEventListener('pointermove', handlePointerMove);
    domElement.addEventListener('pointerup', handlePointerUp);
    domElement.addEventListener('wheel', handleWheel, { passive: false });

    // --- Animation Loop ---
    const clock = new THREE.Clock();
    const animate = () => {
      animFrameRef.current = requestAnimationFrame(animate);

      const delta = clock.getDelta();
      const elapsed = clock.getElapsedTime();

      // Smooth camera interpolation (lerp)
      const st = orbitState.current;
      st.theta += (st.targetTheta - st.theta) * 0.12;
      st.phi += (st.targetPhi - st.phi) * 0.12;
      st.radius += (st.targetRadius - st.radius) * 0.12;

      camera.position.set(
        st.radius * Math.sin(st.theta) * Math.cos(st.phi),
        st.center.y + st.radius * Math.sin(st.phi),
        st.radius * Math.cos(st.theta) * Math.cos(st.phi)
      );
      camera.lookAt(st.center);

      // Animate scene objects & avatar
      scene.animate(elapsed, isSpeakingRef.current, reducedMotionRef.current);

      renderer.render(scene.scene, camera);
    };

    animate();

    // --- Cleanup ---
    return () => {
      if (animFrameRef.current !== null) {
        cancelAnimationFrame(animFrameRef.current);
      }
      resizeObserver.disconnect();
      domElement.removeEventListener('pointerdown', handlePointerDown);
      domElement.removeEventListener('pointermove', handlePointerMove);
      domElement.removeEventListener('pointerup', handlePointerUp);
      domElement.removeEventListener('wheel', handleWheel);

      scene.dispose();
      renderer.dispose();
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }
      sceneRef.current = null;
      rendererRef.current = null;
      cameraRef.current = null;
    };
  }, [is3DView, webglSupported, theme, ambientLight]);

  // Keep 3D scene objects updated when roomData changes
  useEffect(() => {
    if (sceneRef.current && roomData?.objects) {
      sceneRef.current.setObjects(roomData.objects);
    }
  }, [roomData]);

  // Keep selected object highlighted in 3D scene
  useEffect(() => {
    if (sceneRef.current) {
      sceneRef.current.selectObjectById(selectedObject?.object_id || null);
    }
  }, [selectedObject]);

  // --- 6. Configuration Updates ---
  const handleThemeChange = async (newTheme: RoomTheme) => {
    setTheme(newTheme);
    if (sceneRef.current) {
      sceneRef.current.updateTheme(newTheme);
    }
    try {
      await fetch('/api/v1/memory-room/config?profile_id=default-profile-001', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme: newTheme }),
      });
    } catch (e) {
      console.warn('Failed to persist theme preference:', e);
    }
  };

  const handleAmbientLightChange = (intensity: number) => {
    setAmbientLight(intensity);
    if (sceneRef.current) {
      sceneRef.current.setLightIntensity(intensity);
    }
  };

  const handleToggleReducedMotion = async () => {
    const nextMotion = !reducedMotion;
    setReducedMotion(nextMotion);
    try {
      await fetch('/api/v1/memory-room/config?profile_id=default-profile-001', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reduced_motion: nextMotion }),
      });
    } catch {}
  };

  const handleToggleAudio = async () => {
    const nextAudio = !audioEnabled;
    setAudioEnabled(nextAudio);
    try {
      await fetch('/api/v1/memory-room/config?profile_id=default-profile-001', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_enabled: nextAudio }),
      });
    } catch {}
  };

  const handleToggleAvatar = async () => {
    if (!avatarConfig) return;
    const nextEnabled = !avatarConfig.enabled;
    const updated = { ...avatarConfig, enabled: nextEnabled };
    setAvatarConfig(updated);
    if (sceneRef.current) {
      sceneRef.current.updateAvatarConfig(updated);
    }
    try {
      await fetch('/api/v1/avatar/config?profile_id=default-profile-001', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: nextEnabled }),
      });
    } catch {}
  };

  const handleUpdateAvatarConfig = async (updated: Partial<AvatarConfig>) => {
    if (!avatarConfig) return;
    const nextConfig = { ...avatarConfig, ...updated };
    setAvatarConfig(nextConfig);
    if (sceneRef.current) {
      sceneRef.current.updateAvatarConfig(nextConfig);
    }
    try {
      await fetch('/api/v1/avatar/config?profile_id=default-profile-001', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updated),
      });
    } catch (e) {
      console.error('Failed to update avatar configuration:', e);
      throw e;
    }
  };

  const handleTriggerSpeech = async (text: string): Promise<AvatarSpeechResponse | null> => {
    const res = await fetch('/api/v1/avatar/speak?user_id=demo-user-001', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        memorial_profile_id: 'default-profile-001',
        language: 'en',
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Memory Guardian prevented speech generation.');
    }

    const speechData: AvatarSpeechResponse = await res.json();

    // Play synthesized audio and animate avatar
    if (speechData.audio_url && audioEnabled) {
      try {
        if (!audioElementRef.current) {
          audioElementRef.current = new Audio();
        }
        const audio = audioElementRef.current;
        audio.src = speechData.audio_url;
        setIsAvatarSpeaking(true);
        audio.onended = () => {
          setIsAvatarSpeaking(false);
        };
        audio.onerror = () => {
          setIsAvatarSpeaking(false);
        };
        await audio.play();
      } catch (playErr) {
        console.warn('Audio playback not permitted by browser autoplay policy:', playErr);
        setIsAvatarSpeaking(false);
      }
    }

    return speechData;
  };

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowLeft') {
      orbitState.current.targetTheta += 0.05;
    } else if (e.key === 'ArrowRight') {
      orbitState.current.targetTheta -= 0.05;
    } else if (e.key === 'ArrowUp') {
      orbitState.current.targetPhi = Math.min(1.2, orbitState.current.targetPhi + 0.05);
    } else if (e.key === 'ArrowDown') {
      orbitState.current.targetPhi = Math.max(-0.1, orbitState.current.targetPhi - 0.05);
    } else if (e.key === '+' || e.key === '=') {
      orbitState.current.targetRadius = Math.max(2.5, orbitState.current.targetRadius - 0.5);
    } else if (e.key === '-' || e.key === '_') {
      orbitState.current.targetRadius = Math.min(13.0, orbitState.current.targetRadius + 0.5);
    } else if (e.key === 'Home') {
      handleResetCamera();
    }
  };

  return (
    <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 sm:py-8 space-y-6 animate-fadeIn">
      {/* Ethical Banner */}
      <EthicalBanner variant="card" />

        {/* Top Control Bar & Filter HUD */}
        <div className="space-y-3">
          <MemoryRoomControls
            theme={theme}
            onThemeChange={handleThemeChange}
            ambientLight={ambientLight}
            onAmbientLightChange={handleAmbientLightChange}
            onResetCamera={handleResetCamera}
            is3DView={is3DView}
            onToggleView={() => setIs3DView(!is3DView)}
            avatarEnabled={avatarConfig?.enabled || false}
            onToggleAvatar={handleToggleAvatar}
            onOpenAvatarSettings={() => setShowAvatarSettingsModal(true)}
            reducedMotion={reducedMotion}
            onToggleReducedMotion={handleToggleReducedMotion}
            selectedCategory={selectedCategory}
            onCategoryChange={handleCategoryChange}
            audioEnabled={audioEnabled}
            onToggleAudio={handleToggleAudio}
          />

          {/* Search, Filter & Archival Verification Stats Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 text-xs text-slate-400">
            <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 max-w-sm w-full">
              <div className="relative flex-1">
                <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search memory records by title, year, location..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <button
                type="submit"
                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium transition-colors"
              >
                Filter
              </button>
            </form>

            {/* Archival Metrics Summary Badges */}
            {roomData && (
              <div className="flex flex-wrap items-center gap-2">
                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-slate-300 font-medium">
                  <Archive className="w-3.5 h-3.5 text-indigo-400" />
                  <span>{roomData.total_objects} Preserved Anchors</span>
                </span>

                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{roomData.verified_count} Verified</span>
                </span>

                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-950/40 border border-amber-500/30 text-amber-300">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                  <span>{roomData.supported_inference_count} Inferences</span>
                </span>

                {roomData.unknown_count > 0 && (
                  <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-950/40 border border-rose-500/30 text-rose-300">
                    <HelpCircle className="w-3.5 h-3.5 text-rose-400" />
                    <span>{roomData.unknown_count} Unsupported</span>
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        {/* --- Main Viewport State Handling --- */}
        {loading ? (
          <MemoryRoomLoadingState message="Connecting to Vault Storage & Synthesizing 3D Spatial Room..." />
        ) : error ? (
          <MemoryRoomErrorState
            error={error}
            onRetry={() => fetchRoomData()}
            onSwitchToList={() => setIs3DView(false)}
          />
        ) : !roomData || roomData.objects.length === 0 ? (
          // Honest Empty Archive State — Zero Fabrication
          <div className="h-[550px] rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900 via-indigo-950/20 to-slate-950 flex flex-col items-center justify-center p-8 text-center space-y-4 shadow-2xl">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Archive className="w-8 h-8" />
            </div>
            <div className="space-y-1.5 max-w-md">
              <h3 className="font-serif text-lg font-semibold text-slate-100">
                Archival Sanctuary Waiting
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                No memories have been archived for this memorial profile yet. The 3D sanctuary
                remains quietly empty — ECHO never fabricates artificial recollections.
              </p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400">
              <Shield className="w-3.5 h-3.5 text-indigo-400" />
              <span>Evidence-Grounded Principle: Zero Synthetic Memories</span>
            </div>
          </div>
        ) : is3DView ? (
          // --- Interactive 3D Spatial Canvas Viewport ---
          <div
            tabIndex={0}
            onKeyDown={handleKeyDown}
            className="relative h-[600px] rounded-3xl border border-slate-800 bg-slate-950 overflow-hidden shadow-2xl focus:outline-none focus:ring-1 focus:ring-indigo-500 group select-none"
          >
            {/* Canvas Mount Container */}
            <div
              ref={containerRef}
              className="absolute inset-0 cursor-grab active:cursor-grabbing w-full h-full"
            />

            {/* Top Left HUD: Spatial Compass & Status */}
            <div className="absolute top-4 left-4 z-10 flex flex-col gap-2 pointer-events-none">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/85 border border-slate-800 text-xs text-slate-200 backdrop-blur-md shadow-lg pointer-events-auto">
                <Compass className="w-3.5 h-3.5 text-indigo-400 animate-spin-slow" />
                <span className="font-medium">
                  {theme.replace(/_/g, ' ')} &bull; 3D Interactive Sanctuary
                </span>
              </div>

              {avatarConfig?.enabled && (
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-purple-950/80 border border-purple-500/40 text-[11px] text-purple-300 backdrop-blur-md shadow-lg pointer-events-auto">
                  <Sparkles className="w-3 h-3 text-purple-400" />
                  <span>
                    Presence Guide Active: {avatarConfig.display_name}
                  </span>
                </div>
              )}
            </div>

            {/* Top Right HUD: Watermark Disclosure Banner */}
            <div className="absolute top-4 right-4 z-10 max-w-xs pointer-events-none">
              <div className="px-3 py-1.5 rounded-xl bg-slate-900/90 border border-amber-500/40 text-[10px] text-amber-300/90 backdrop-blur-md shadow-lg font-medium leading-tight">
                AI-GENERATED MEMORIAL REPRESENTATION &bull; NOT THE ACTUAL PERSON
              </div>
            </div>

            {/* Bottom HUD: Dynamic Selection & Inspection Bar */}
            <div className="absolute bottom-4 inset-x-4 z-10 flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800/90 backdrop-blur-md shadow-2xl text-xs text-slate-300 pointer-events-auto">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
                  <Eye className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-[11px] text-slate-500">
                    {selectedObject
                      ? 'Selected Archival Anchor:'
                      : hoveredObject
                      ? 'Hovered Object:'
                      : 'Spatial Navigation Guide:'}
                  </div>
                  <div className="font-semibold text-slate-100 flex items-center gap-2">
                    <span>
                      {selectedObject
                        ? selectedObject.title
                        : hoveredObject
                        ? hoveredObject.title
                        : 'Click any photo, audio tape, or book to inspect preserved evidence.'}
                    </span>
                    {(selectedObject?.is_demo_placeholder || hoveredObject?.is_demo_placeholder) && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-500/30">
                        Demo Placeholder
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Navigation Hints */}
              <div className="flex items-center gap-3 text-[11px] text-slate-400">
                <span className="hidden sm:inline">
                  Drag to Orbit &bull; Scroll to Zoom &bull; Click to Select
                </span>
                <button
                  onClick={handleResetCamera}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 flex items-center gap-1.5 transition-colors"
                  title="Reset 3D Camera"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Reset View</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          // --- Accessible 2D Fallback List View ---
          <AccessibleMemoryList
            objects={roomData.objects}
            selectedObject={selectedObject}
            onSelectObject={(obj) => setSelectedObject(obj)}
            onOpenDetails={(obj) => setSelectedObject(obj)}
          />
        )}

        {/* --- Chronological Milestone Timeline Panel --- */}
        {roomData && roomData.objects.length > 0 && (
          <MemoryTimelinePanel
            objects={roomData.objects}
            selectedObject={selectedObject}
            onSelectObject={(obj) => {
              setSelectedObject(obj);
              if (sceneRef.current) {
                sceneRef.current.selectObjectById(obj.object_id);
              }
            }}
          />
        )}

      {/* --- Memory Object Details Drawer --- */}
      <MemoryObjectDetails
        object={selectedObject}
        onClose={() => {
          setSelectedObject(null);
          if (sceneRef.current) {
            sceneRef.current.selectObjectById(null);
          }
        }}
        onOpenEvidenceModal={() => setShowEvidenceModal(true)}
      />

      {/* --- Provenance and Evidence Modal --- */}
      {showEvidenceModal && (
        <MemoryEvidencePanel
          object={selectedObject}
          onClose={() => setShowEvidenceModal(false)}
        />
      )}

      {/* --- Memorial Avatar Settings & Voice Modal --- */}
      {showAvatarSettingsModal && avatarConfig && (
        <AvatarSettingsPanel
          avatarConfig={avatarConfig}
          onUpdateConfig={handleUpdateAvatarConfig}
          onTriggerSpeech={handleTriggerSpeech}
          onClose={() => setShowAvatarSettingsModal(false)}
        />
      )}
    </div>
  );
}
