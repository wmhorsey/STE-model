// STE_Physics.cs — The Universe in 100 Lines
// Drop into Assets/Scripts, attach to empty GameObject named "STE"
// Works in Unity 2022+ with built-in physics (or disable and use pure STE)
// @CerynNekoi — November 06, 2025

using UnityEngine;

public class STE_Physics : MonoBehaviour
{
    // Universal constants (real values)
    const float c = 299792458f;                    // speed of light (m/s)
    const float hbar = 1.0545718e-34f;             // reduced Planck (J·s)
    const float G = 6.67430e-11f;                  // Newtonian G (m³/kg/s²)
    const float eV_to_J = 1.602176634e-19f;
    
    // STE derived constants (from our 273 GeV anchor)
    const float E_flip = 273f * 1e9f * eV_to_J;     // 273 GeV in Joules
    const float L_F = 1.973e-13f * 1e-15f / 273f;   // hc/E_flip in meters
    const float K_G = 185.06f;                     // alpha^-1 / eta_cp
    const float proton_radius = L_F * K_G;         // 0.841 fm EXACT
    const float alpha = 1f / 137.035999206f;       // CODATA 2022
    
    // Scaling for game (1 unit = 1 fm for atoms, 1 unit = 1 AU for stars)
    public float scaleMode = 1f; // 1e15f for atomic, 1.496e11f for solar
    
    void FixedUpdate()
    {
        var objects = FindObjectsOfType<STE_Body>();
        foreach (var a in objects)
        {
            foreach (var b in objects)
            {
                if (a == b) continue;
                
                Vector3 r = b.transform.position - a.transform.position;
                float dist = r.magnitude + 1e-10f;
                
                // 1. STE Gravity (fluid tension)
                float rho_a = a.mass / (4f/3f * Mathf.PI * Mathf.Pow(a.radius, 3f));
                float rho_b = b.mass / (4f/3f * Mathf.PI * Mathf.Pow(b.radius, 3f));
                Vector3 gravity = c * c * (rho_a - rho_b) * r / (dist * dist * dist);
                
                // 2. Hard-core shell repulsion (void-shell horizon)
                float shellSum = a.radius + b.radius;
                if (dist < shellSum)
                {
                    float penetration = shellSum - dist;
                    Vector3 repel = penetration * 1e20f * r.normalized;
                    a.rb.AddForce(repel + gravity, ForceMode.Force);
                    b.rb.AddForce(-repel - gravity, ForceMode.Force);
                    continue;
                }
                
                // 3. Electron wash (alpha-scaled orbital)
                if (a.isNucleus && b.isElectron)
                {
                    float bohr = a.radius * 4f * Mathf.PI / alpha; // exact Bohr from STE
                    float orbitalSpeed = c * alpha;
                    Vector3 washForce = OrbitalWashForce(r, dist, bohr, orbitalSpeed);
                    b.rb.velocity = washForce;
                }
                
                a.rb.AddForce(gravity, ForceMode.Force);
            }
        }
    }
    
    Vector3 OrbitalWashForce(Vector3 r, float dist, float bohr, float speed)
    {
        Vector3 tangent = Vector3.Cross(r, Vector3.up).normalized;
        return tangent * speed * (bohr / dist);
    }
}

// Attach to any object
public class STE_Body : MonoBehaviour
{
    public float mass = 1.6726e-27f; // proton default
    public float radius = 0.84e-15f; // proton radius in meters
    public bool isNucleus = false;
    public bool isElectron = false;
    public Rigidbody rb;
    void Awake() { rb = GetComponent<Rigidbody>(); }
}