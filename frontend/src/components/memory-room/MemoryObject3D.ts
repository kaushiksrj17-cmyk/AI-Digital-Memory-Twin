import * as THREE from 'three';
import { RoomObject, RoomObjectType, ConfidenceLevel } from '@/types';

export class MemoryObject3D {
  public group: THREE.Group;
  public objectData: RoomObject;
  private primaryMesh: THREE.Mesh;
  private glowRing?: THREE.Mesh;
  private isSelected: boolean = false;
  private isHovered: boolean = false;

  constructor(objectData: RoomObject) {
    this.objectData = objectData;
    this.group = new THREE.Group();
    this.group.position.set(
      objectData.position.x,
      objectData.position.y,
      objectData.position.z
    );

    if (objectData.rotation) {
      this.group.rotation.set(
        objectData.rotation.x,
        objectData.rotation.y,
        objectData.rotation.z
      );
    }

    // Determine confidence accent color
    const accentColor =
      objectData.confidence === 'VERIFIED'
        ? 0x10b981 // Emerald
        : objectData.confidence === 'SUPPORTED_INFERENCE'
        ? 0xf59e0b // Amber
        : 0xef4444; // Rose

    // Build specialized 3D geometry based on object type
    this.primaryMesh = this.createMeshForType(objectData.object_type, accentColor);
    this.primaryMesh.castShadow = true;
    this.primaryMesh.receiveShadow = true;

    // Attach reference for raycasting
    this.primaryMesh.userData = {
      isMemoryObject: true,
      objectData: this.objectData,
      instance: this,
    };

    this.group.add(this.primaryMesh);

    // Add subtle floor anchor shadow / glow ring
    this.addGlowRing(accentColor);
  }

  private createMeshForType(type: RoomObjectType, accentColor: number): THREE.Mesh {
    switch (type) {
      case 'PHOTO_FRAME': {
        // Picture frame with inner canvas
        const frameGeo = new THREE.BoxGeometry(0.85, 1.1, 0.08);
        const frameMat = new THREE.MeshStandardMaterial({
          color: 0x27272a,
          roughness: 0.4,
          metalness: 0.2,
          emissive: accentColor,
          emissiveIntensity: 0.08,
        });
        const frame = new THREE.Mesh(frameGeo, frameMat);

        // Inner photo surface
        const innerGeo = new THREE.PlaneGeometry(0.72, 0.95);
        const innerMat = new THREE.MeshStandardMaterial({
          color: 0xe2e8f0,
          roughness: 0.9,
        });
        const inner = new THREE.Mesh(innerGeo, innerMat);
        inner.position.z = 0.045;
        frame.add(inner);

        return frame;
      }

      case 'ARCHIVE_BOOKSHELF': {
        // Set of archival books / binder box
        const bookGeo = new THREE.BoxGeometry(0.3, 0.75, 0.55);
        const bookMat = new THREE.MeshStandardMaterial({
          color: 0x78350f,
          roughness: 0.6,
          emissive: accentColor,
          emissiveIntensity: 0.08,
        });
        const book = new THREE.Mesh(bookGeo, bookMat);

        // Spine detail
        const spineGeo = new THREE.BoxGeometry(0.04, 0.73, 0.53);
        const spineMat = new THREE.MeshStandardMaterial({ color: 0xd97706 });
        const spine = new THREE.Mesh(spineGeo, spineMat);
        spine.position.x = -0.14;
        book.add(spine);

        return book;
      }

      case 'AUDIO_STATION': {
        // Vintage audio reel console
        const consoleGeo = new THREE.CylinderGeometry(0.42, 0.45, 0.25, 24);
        const consoleMat = new THREE.MeshStandardMaterial({
          color: 0x1e293b,
          roughness: 0.3,
          metalness: 0.6,
          emissive: 0x06b6d4,
          emissiveIntensity: 0.15,
        });
        const consoleMesh = new THREE.Mesh(consoleGeo, consoleMat);

        // Top Reel
        const reelGeo = new THREE.TorusGeometry(0.24, 0.03, 12, 24);
        const reelMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8 });
        const reel = new THREE.Mesh(reelGeo, reelMat);
        reel.rotation.x = Math.PI / 2;
        reel.position.y = 0.13;
        consoleMesh.add(reel);

        return consoleMesh;
      }

      case 'TIMELINE_WALL': {
        // Chronological wall milestone marker
        const markerGeo = new THREE.CylinderGeometry(0.28, 0.28, 0.06, 24);
        const markerMat = new THREE.MeshStandardMaterial({
          color: 0x312e81,
          roughness: 0.4,
          emissive: accentColor,
          emissiveIntensity: 0.2,
        });
        const marker = new THREE.Mesh(markerGeo, markerMat);
        marker.rotation.x = Math.PI / 2;
        return marker;
      }

      case 'STORY_STATION': {
        // Open manuscript / book stand
        const standGeo = new THREE.BoxGeometry(0.65, 0.08, 0.45);
        const standMat = new THREE.MeshStandardMaterial({
          color: 0xa855f7,
          roughness: 0.5,
          emissive: accentColor,
          emissiveIntensity: 0.1,
        });
        return new THREE.Mesh(standGeo, standMat);
      }

      default: {
        // Central Display / Desk Keepsake Box
        const boxGeo = new THREE.BoxGeometry(0.5, 0.5, 0.5);
        const boxMat = new THREE.MeshStandardMaterial({
          color: 0x4f46e5,
          roughness: 0.3,
          metalness: 0.3,
          emissive: accentColor,
          emissiveIntensity: 0.15,
        });
        return new THREE.Mesh(boxGeo, boxMat);
      }
    }
  }

  private addGlowRing(color: number) {
    const ringGeo = new THREE.RingGeometry(0.35, 0.42, 24);
    const ringMat = new THREE.MeshBasicMaterial({
      color,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.35,
    });
    this.glowRing = new THREE.Mesh(ringGeo, ringMat);
    this.glowRing.rotation.x = -Math.PI / 2;
    this.glowRing.position.y = -0.55;
    this.group.add(this.glowRing);
  }

  public setHovered(hovered: boolean) {
    this.isHovered = hovered;
    this.updateHighlightState();
  }

  public setSelected(selected: boolean) {
    this.isSelected = selected;
    this.updateHighlightState();
  }

  private updateHighlightState() {
    const mat = this.primaryMesh.material as THREE.MeshStandardMaterial;
    if (this.isSelected) {
      mat.emissiveIntensity = 0.6;
      this.group.scale.set(1.1, 1.1, 1.1);
      if (this.glowRing) (this.glowRing.material as THREE.MeshBasicMaterial).opacity = 0.8;
    } else if (this.isHovered) {
      mat.emissiveIntensity = 0.35;
      this.group.scale.set(1.04, 1.04, 1.04);
      if (this.glowRing) (this.glowRing.material as THREE.MeshBasicMaterial).opacity = 0.6;
    } else {
      mat.emissiveIntensity = 0.08;
      this.group.scale.set(1.0, 1.0, 1.0);
      if (this.glowRing) (this.glowRing.material as THREE.MeshBasicMaterial).opacity = 0.35;
    }
  }

  public animate(elapsedTime: number, reducedMotion: boolean = false) {
    if (reducedMotion) return;

    // Subtle gentle float for non-wall items
    if (
      this.objectData.object_type !== 'PHOTO_FRAME' &&
      this.objectData.object_type !== 'TIMELINE_WALL'
    ) {
      this.group.position.y =
        this.objectData.position.y + Math.sin(elapsedTime * 1.5 + this.objectData.position.x) * 0.02;
    }
  }

  public dispose() {
    this.primaryMesh.geometry.dispose();
    if (Array.isArray(this.primaryMesh.material)) {
      this.primaryMesh.material.forEach((m) => m.dispose());
    } else {
      this.primaryMesh.material.dispose();
    }
    if (this.glowRing) {
      this.glowRing.geometry.dispose();
      (this.glowRing.material as THREE.Material).dispose();
    }
  }
}
