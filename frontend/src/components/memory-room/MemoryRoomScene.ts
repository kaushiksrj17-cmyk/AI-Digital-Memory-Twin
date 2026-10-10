import * as THREE from 'three';
import { RoomEnvironment } from './RoomEnvironment';
import { MemoryObject3D } from './MemoryObject3D';
import { MemorialAvatar3D } from './MemorialAvatar3D';
import { RoomObject, RoomTheme, AvatarConfig } from '@/types';

export class MemoryRoomScene {
  public scene: THREE.Scene;
  private environment: RoomEnvironment;
  private objectInstances: Map<string, MemoryObject3D> = new Map();
  private avatarInstance?: MemorialAvatar3D;
  private raycaster: THREE.Raycaster;
  private mouseVector: THREE.Vector2;
  private hoveredInstance?: MemoryObject3D;
  private selectedInstance?: MemoryObject3D;
  private onSelectCallback?: (obj: RoomObject | null) => void;
  private onHoverCallback?: (obj: RoomObject | null) => void;

  constructor(
    theme: RoomTheme = 'ARCHIVAL_WARM',
    ambientLight: number = 0.8,
    avatarConfig?: AvatarConfig
  ) {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x090d16);

    // Initialize 3D architectural environment
    this.environment = new RoomEnvironment(theme, ambientLight);
    this.scene.add(this.environment.getGroup());

    // Initialize optional Memorial Avatar
    if (avatarConfig) {
      this.avatarInstance = new MemorialAvatar3D(avatarConfig);
      this.scene.add(this.avatarInstance.group);
    }

    // Raycaster for user interaction
    this.raycaster = new THREE.Raycaster();
    this.mouseVector = new THREE.Vector2();
  }

  public setObjects(objects: RoomObject[]) {
    // Clear existing objects
    this.objectInstances.forEach((inst) => {
      this.scene.remove(inst.group);
      inst.dispose();
    });
    this.objectInstances.clear();

    // Populate new objects
    objects.forEach((obj) => {
      const inst = new MemoryObject3D(obj);
      this.objectInstances.set(obj.object_id, inst);
      this.scene.add(inst.group);
    });
  }

  public setCallbacks(
    onSelect: (obj: RoomObject | null) => void,
    onHover: (obj: RoomObject | null) => void
  ) {
    this.onSelectCallback = onSelect;
    this.onHoverCallback = onHover;
  }

  public updateTheme(theme: RoomTheme) {
    this.environment.updateTheme(theme);
  }

  public setLightIntensity(intensity: number) {
    this.environment.setLightIntensity(intensity);
  }

  public updateAvatarConfig(config: AvatarConfig) {
    if (this.avatarInstance) {
      this.avatarInstance.updateConfig(config);
    }
  }

  public selectObjectById(objectId: string | null) {
    if (this.selectedInstance) {
      this.selectedInstance.setSelected(false);
      this.selectedInstance = undefined;
    }

    if (objectId && this.objectInstances.has(objectId)) {
      const inst = this.objectInstances.get(objectId)!;
      inst.setSelected(true);
      this.selectedInstance = inst;
      if (this.avatarInstance) {
        this.avatarInstance.setLookAtTarget(inst.group.position);
      }
    } else {
      if (this.avatarInstance) {
        this.avatarInstance.setLookAtTarget(undefined);
      }
    }
  }

  public handlePointerMove(normalizedX: number, normalizedY: number, camera: THREE.Camera) {
    this.mouseVector.set(normalizedX, normalizedY);
    this.raycaster.setFromCamera(this.mouseVector, camera);

    const interactiveMeshes: THREE.Object3D[] = [];
    this.objectInstances.forEach((inst) => {
      inst.group.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          interactiveMeshes.push(child);
        }
      });
    });

    const intersects = this.raycaster.intersectObjects(interactiveMeshes, true);

    if (intersects.length > 0) {
      let hitInstance: MemoryObject3D | undefined;
      let curr: THREE.Object3D | null = intersects[0].object;
      while (curr && !hitInstance) {
        if (curr.userData && curr.userData.instance) {
          hitInstance = curr.userData.instance;
        }
        curr = curr.parent;
      }

      if (hitInstance !== this.hoveredInstance) {
        if (this.hoveredInstance) this.hoveredInstance.setHovered(false);
        this.hoveredInstance = hitInstance;
        if (this.hoveredInstance) this.hoveredInstance.setHovered(true);
        if (this.onHoverCallback) {
          this.onHoverCallback(hitInstance ? hitInstance.objectData : null);
        }
      }
    } else {
      if (this.hoveredInstance) {
        this.hoveredInstance.setHovered(false);
        this.hoveredInstance = undefined;
        if (this.onHoverCallback) this.onHoverCallback(null);
      }
    }
  }

  public handlePointerClick(normalizedX: number, normalizedY: number, camera: THREE.Camera) {
    this.mouseVector.set(normalizedX, normalizedY);
    this.raycaster.setFromCamera(this.mouseVector, camera);

    const interactiveMeshes: THREE.Object3D[] = [];
    this.objectInstances.forEach((inst) => {
      inst.group.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          interactiveMeshes.push(child);
        }
      });
    });

    const intersects = this.raycaster.intersectObjects(interactiveMeshes, true);

    if (intersects.length > 0) {
      let hitInstance: MemoryObject3D | undefined;
      let curr: THREE.Object3D | null = intersects[0].object;
      while (curr && !hitInstance) {
        if (curr.userData && curr.userData.instance) {
          hitInstance = curr.userData.instance;
        }
        curr = curr.parent;
      }

      if (hitInstance) {
        this.selectObjectById(hitInstance.objectData.object_id);
        if (this.onSelectCallback) {
          this.onSelectCallback(hitInstance.objectData);
        }
        return;
      }
    }

    // Deselect if clicked empty space
    this.selectObjectById(null);
    if (this.onSelectCallback) {
      this.onSelectCallback(null);
    }
  }

  public animate(
    elapsedTime: number,
    isSpeaking: boolean = false,
    reducedMotion: boolean = false
  ) {
    // Animate memory objects
    this.objectInstances.forEach((inst) => {
      inst.animate(elapsedTime, reducedMotion);
    });

    // Animate avatar
    if (this.avatarInstance) {
      this.avatarInstance.animate(elapsedTime, isSpeaking, reducedMotion);
    }
  }

  public dispose() {
    this.environment.dispose();
    this.objectInstances.forEach((inst) => inst.dispose());
    this.objectInstances.clear();
    if (this.avatarInstance) {
      this.avatarInstance.dispose();
    }
  }
}
