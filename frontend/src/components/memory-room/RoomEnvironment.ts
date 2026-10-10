import * as THREE from 'three';
import { RoomTheme } from '@/types';

export interface ThemeColors {
  wall: number;
  floor: number;
  ambient: number;
  accent: number;
}

export const THEME_COLOR_MAP: Record<RoomTheme, ThemeColors> = {
  ARCHIVAL_WARM: {
    wall: 0x1e293b,
    floor: 0x5c2b0e,
    ambient: 0xfef3c7,
    accent: 0xf59e0b,
  },
  STUDY_CLASSIC: {
    wall: 0x172554,
    floor: 0x3e1806,
    ambient: 0xfde68a,
    accent: 0xd97706,
  },
  GALLERY_MODERN: {
    wall: 0x0f172a,
    floor: 0x334155,
    ambient: 0xe2e8f0,
    accent: 0x6366f1,
  },
  MINIMAL_SERENE: {
    wall: 0x18181b,
    floor: 0x3f3f46,
    ambient: 0xf4f4f5,
    accent: 0x10b981,
  },
};

export class RoomEnvironment {
  private group: THREE.Group;
  private floorMesh: THREE.Mesh;
  private backWallMesh: THREE.Mesh;
  private leftWallMesh: THREE.Mesh;
  private rightWallMesh: THREE.Mesh;
  private ambientLight: THREE.AmbientLight;
  private dirLight: THREE.DirectionalLight;
  private warmPointLight: THREE.PointLight;

  constructor(theme: RoomTheme = 'ARCHIVAL_WARM', lightIntensity: number = 0.8) {
    this.group = new THREE.Group();
    const colors = THEME_COLOR_MAP[theme] || THEME_COLOR_MAP.ARCHIVAL_WARM;

    // --- Floor ---
    const floorGeo = new THREE.PlaneGeometry(16, 16);
    const floorMat = new THREE.MeshStandardMaterial({
      color: colors.floor,
      roughness: 0.6,
      metalness: 0.1,
    });
    this.floorMesh = new THREE.Mesh(floorGeo, floorMat);
    this.floorMesh.rotation.x = -Math.PI / 2;
    this.floorMesh.position.y = 0;
    this.floorMesh.receiveShadow = true;
    this.group.add(this.floorMesh);

    // Floor Baseboard Accent
    const floorGrid = new THREE.GridHelper(16, 16, 0x334155, 0x1e293b);
    floorGrid.position.y = 0.01;
    this.group.add(floorGrid);

    // --- Back Wall (North Gallery) ---
    const backWallGeo = new THREE.PlaneGeometry(16, 7);
    const wallMat = new THREE.MeshStandardMaterial({
      color: colors.wall,
      roughness: 0.8,
      metalness: 0.05,
    });
    this.backWallMesh = new THREE.Mesh(backWallGeo, wallMat);
    this.backWallMesh.position.set(0, 3.5, -6.5);
    this.group.add(this.backWallMesh);

    // --- Left Wall (West Audio Zone) ---
    const leftWallGeo = new THREE.PlaneGeometry(16, 7);
    this.leftWallMesh = new THREE.Mesh(leftWallGeo, wallMat);
    this.leftWallMesh.rotation.y = Math.PI / 2;
    this.leftWallMesh.position.set(-6.5, 3.5, 0);
    this.group.add(this.leftWallMesh);

    // --- Right Wall (East Archive Shelves) ---
    const rightWallGeo = new THREE.PlaneGeometry(16, 7);
    this.rightWallMesh = new THREE.Mesh(rightWallGeo, wallMat);
    this.rightWallMesh.rotation.y = -Math.PI / 2;
    this.rightWallMesh.position.set(6.5, 3.5, 0);
    this.group.add(this.rightWallMesh);

    // --- Architectural Desk / Study Plinth in Center ---
    const deskGeo = new THREE.BoxGeometry(3.6, 0.75, 1.6);
    const deskMat = new THREE.MeshStandardMaterial({
      color: colors.floor,
      roughness: 0.5,
      metalness: 0.1,
    });
    const desk = new THREE.Mesh(deskGeo, deskMat);
    desk.position.set(0, 0.375, -0.2);
    desk.receiveShadow = true;
    desk.castShadow = true;
    this.group.add(desk);

    // --- Soft Ambient Lighting ---
    this.ambientLight = new THREE.AmbientLight(colors.ambient, lightIntensity);
    this.group.add(this.ambientLight);

    // Natural Key Directional Light
    this.dirLight = new THREE.DirectionalLight(0xffffff, lightIntensity * 0.9);
    this.dirLight.position.set(5, 8, 5);
    this.dirLight.castShadow = true;
    this.group.add(this.dirLight);

    // Warm Reading Lantern Point Light
    this.warmPointLight = new THREE.PointLight(colors.accent, lightIntensity * 1.2, 10);
    this.warmPointLight.position.set(0, 2.8, -0.2);
    this.group.add(this.warmPointLight);
  }

  public getGroup(): THREE.Group {
    return this.group;
  }

  public updateTheme(theme: RoomTheme) {
    const colors = THEME_COLOR_MAP[theme] || THEME_COLOR_MAP.ARCHIVAL_WARM;
    (this.floorMesh.material as THREE.MeshStandardMaterial).color.setHex(colors.floor);
    (this.backWallMesh.material as THREE.MeshStandardMaterial).color.setHex(colors.wall);
    (this.leftWallMesh.material as THREE.MeshStandardMaterial).color.setHex(colors.wall);
    (this.rightWallMesh.material as THREE.MeshStandardMaterial).color.setHex(colors.wall);
    this.ambientLight.color.setHex(colors.ambient);
    this.warmPointLight.color.setHex(colors.accent);
  }

  public setLightIntensity(intensity: number) {
    this.ambientLight.intensity = intensity;
    this.dirLight.intensity = intensity * 0.9;
    this.warmPointLight.intensity = intensity * 1.2;
  }

  public dispose() {
    this.floorMesh.geometry.dispose();
    (this.floorMesh.material as THREE.Material).dispose();

    this.backWallMesh.geometry.dispose();
    (this.backWallMesh.material as THREE.Material).dispose();

    this.leftWallMesh.geometry.dispose();
    this.rightWallMesh.geometry.dispose();
  }
}
