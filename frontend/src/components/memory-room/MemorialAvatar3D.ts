import * as THREE from 'three';
import { AvatarConfig, AvatarModelType, AvatarPose } from '@/types';

export class MemorialAvatar3D {
  public group: THREE.Group;
  private headMesh: THREE.Mesh;
  private torsoMesh: THREE.Mesh;
  private jawMesh: THREE.Mesh;
  private haloMesh: THREE.Mesh;
  private labelSprite?: THREE.Sprite;
  private avatarConfig: AvatarConfig;
  private targetLookAt?: THREE.Vector3;

  constructor(avatarConfig: AvatarConfig) {
    this.avatarConfig = avatarConfig;
    this.group = new THREE.Group();
    this.group.position.set(
      avatarConfig.position.x,
      avatarConfig.position.y,
      avatarConfig.position.z
    );

    // Build stylized respectful memorial representation
    const { torso, head, jaw, halo } = this.buildCharacterMesh(avatarConfig.model_type);
    this.torsoMesh = torso;
    this.headMesh = head;
    this.jawMesh = jaw;
    this.haloMesh = halo;

    this.group.add(this.torsoMesh);
    this.group.add(this.headMesh);
    this.group.add(this.haloMesh);

    // Create subtle overhead 3D text disclosure banner sprite
    this.createFloatingDisclosureLabel();

    this.group.visible = avatarConfig.enabled;
  }

  private buildCharacterMesh(modelType: AvatarModelType) {
    const isSilhouette = modelType === 'NEUTRAL_SILHOUETTE';

    // Materials
    const skinMat = new THREE.MeshStandardMaterial({
      color: isSilhouette ? 0x93c5fd : 0xf1f5f9,
      roughness: 0.5,
      metalness: 0.1,
      transparent: isSilhouette,
      opacity: isSilhouette ? 0.65 : 1.0,
      emissive: isSilhouette ? 0x3b82f6 : 0x000000,
      emissiveIntensity: isSilhouette ? 0.2 : 0.0,
    });

    const clothMat = new THREE.MeshStandardMaterial({
      color: isSilhouette ? 0x1e3a8a : 0x334155,
      roughness: 0.7,
      transparent: isSilhouette,
      opacity: isSilhouette ? 0.75 : 1.0,
    });

    // 1. Torso & Shoulders
    const torsoGeo = new THREE.CylinderGeometry(0.32, 0.26, 1.1, 16);
    const torso = new THREE.Mesh(torsoGeo, clothMat);
    torso.position.y = 0.85;
    torso.castShadow = true;

    // Shoulders
    const shoulderGeo = new THREE.CapsuleGeometry(0.2, 0.6, 8, 16);
    const shoulders = new THREE.Mesh(shoulderGeo, clothMat);
    shoulders.rotation.z = Math.PI / 2;
    shoulders.position.y = 0.45;
    torso.add(shoulders);

    // 2. Head
    const headGeo = new THREE.SphereGeometry(0.24, 20, 20);
    const head = new THREE.Mesh(headGeo, skinMat);
    head.position.y = 1.62;
    head.castShadow = true;

    // 3. Subtle Jaw / Mouth for speech animation
    const jawGeo = new THREE.BoxGeometry(0.12, 0.04, 0.12);
    const jawMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1 });
    const jaw = new THREE.Mesh(jawGeo, jawMat);
    jaw.position.set(0, -0.16, 0.14);
    head.add(jaw);

    // 4. Respectful Ambient Halo / Soft Memorial Aura
    const haloGeo = new THREE.TorusGeometry(0.32, 0.015, 12, 32);
    const haloMat = new THREE.MeshBasicMaterial({
      color: 0x818cf8,
      transparent: true,
      opacity: 0.4,
    });
    const halo = new THREE.Mesh(haloGeo, haloMat);
    halo.rotation.x = Math.PI / 2;
    halo.position.y = 1.95;

    return { torso, head, jaw, halo };
  }

  private createFloatingDisclosureLabel() {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Background pill
    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    ctx.roundRect(16, 20, 480, 88, 24);
    ctx.fill();

    // Border
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.6)';
    ctx.lineWidth = 4;
    ctx.roundRect(16, 20, 480, 88, 24);
    ctx.stroke();

    // Text
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('AI-GENERATED MEMORIAL AVATAR', 256, 58);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '16px sans-serif';
    ctx.fillText('Not the actual person • Evidence-grounded guide', 256, 88);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true });
    this.labelSprite = new THREE.Sprite(spriteMat);
    this.labelSprite.position.set(0, 2.3, 0);
    this.labelSprite.scale.set(1.8, 0.45, 1);
    this.group.add(this.labelSprite);
  }

  public setLookAtTarget(targetPosition?: THREE.Vector3) {
    this.targetLookAt = targetPosition;
  }

  public updateConfig(config: AvatarConfig) {
    this.avatarConfig = config;
    this.group.visible = config.enabled;
  }

  public animate(elapsedTime: number, isSpeaking: boolean = false, reducedMotion: boolean = false) {
    if (!this.avatarConfig.enabled) return;

    if (!reducedMotion) {
      // 1. Idle breathing
      const breath = Math.sin(elapsedTime * 1.8) * 0.015;
      this.torsoMesh.position.y = 0.85 + breath;
      this.headMesh.position.y = 1.62 + breath;
      this.haloMesh.position.y = 1.95 + breath;

      // 2. Head turning towards selected target if present
      if (this.targetLookAt) {
        const dx = this.targetLookAt.x - this.group.position.x;
        const dz = this.targetLookAt.z - this.group.position.z;
        const targetAngle = Math.atan2(dx, dz);
        this.headMesh.rotation.y = THREE.MathUtils.lerp(this.headMesh.rotation.y, targetAngle, 0.04);
      } else {
        // Return to forward
        this.headMesh.rotation.y = THREE.MathUtils.lerp(this.headMesh.rotation.y, 0, 0.03);
      }

      // 3. Speaking animation
      if (isSpeaking || this.avatarConfig.is_speaking) {
        const mouthOpen = (Math.sin(elapsedTime * 14) + 1) * 0.02;
        this.jawMesh.position.y = -0.16 - mouthOpen;
      } else {
        this.jawMesh.position.y = -0.16;
      }

      // 4. Subtle halo float
      this.haloMesh.rotation.z = elapsedTime * 0.2;
    }
  }

  public dispose() {
    this.torsoMesh.geometry.dispose();
    this.headMesh.geometry.dispose();
    this.jawMesh.geometry.dispose();
    this.haloMesh.geometry.dispose();
  }
}
