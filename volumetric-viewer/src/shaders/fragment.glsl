#version 460 core

uniform sampler3D volumeTex; 
uniform vec3 cameraPos;        
uniform sampler1D transferFuncTex;
uniform vec3 volumeScale;  // scale used to adapt volume to cube 1x1x1  
uniform vec3 volumeColor; // color when in isovalue view
uniform float minIsovalueLimit;
uniform float maxIsovalueLimit;
uniform int viewMode; // o for isovalue view / 1 for transfer func

in vec3 fragPos;               
out vec4 outColor;

const float STEP_SIZE = 0.0001;
const float ALPHA_THRESHOLD = 0.95;

vec4 transferFunction(float density) {
    return texture(transferFuncTex, density);
}

bool intersectBox(vec3 rayOrigin, vec3 rayDir, out float tEnter, out float tExit) {
    vec3 invDir = 1.0 / rayDir;
    vec3 t0 = (vec3(0.0) - rayOrigin) * invDir;
    vec3 t1 = (vec3(1.0) - rayOrigin) * invDir;

    vec3 tmin = min(t0, t1);
    vec3 tmax = max(t0, t1);

    tEnter = max(max(tmin.x, tmin.y), tmin.z);
    tExit  = min(min(tmax.x, tmax.y), tmax.z);

    return tEnter <= tExit;
}

void main() {
    vec3 rayDir = normalize((fragPos - cameraPos) / volumeScale);
    
    float tEnter, tExit;
    if (!intersectBox(cameraPos / volumeScale, rayDir, tEnter, tExit)) {
        discard;
    }

    tEnter = max(tEnter, 0.0);
    vec3 pos = cameraPos / volumeScale + rayDir * tEnter;
    float t = tEnter;

    vec4 accumulatedColor = vec4(0.0);

    while (t < tExit) {
        float density = texture(volumeTex, pos).r;
        vec4 sampleColor;

        if (viewMode == 0) {
            sampleColor = (density > minIsovalueLimit && density < maxIsovalueLimit) ? vec4(volumeColor, density) : vec4(volumeColor, 0.0);
        } else {
            sampleColor = transferFunction(density);
        }

        float sigma = sampleColor.a*50.0;
        vec3 emiss = sampleColor.rgb;
        float alpha = 1.0 - exp(-sigma*STEP_SIZE);

        accumulatedColor.rgb += (1.0 - accumulatedColor.a) * emiss * alpha;
        accumulatedColor.a += (1.0 - accumulatedColor.a) * alpha;

        if (accumulatedColor.a >= ALPHA_THRESHOLD)
            break;

        t += STEP_SIZE;
        pos += rayDir * STEP_SIZE;
    }

    outColor = accumulatedColor;
}
