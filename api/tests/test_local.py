import requests
import time

def test_reset_queue_local():
    """Test de l'endpoint reset-queue en local"""
    try:
        # Appel de l'endpoint
        response = requests.get("http://localhost/reset-queue")
        
        # Affichage des résultats
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Test réussi : La file d'attente a été réinitialisée")
        else:
            print("❌ Test échoué : Erreur lors de la réinitialisation")
            print(f"Message d'erreur : {response.json().get('detail', 'Pas de détail')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion : Vérifiez que les containers sont bien lancés")
    except Exception as e:
        print(f"❌ Erreur inattendue : {str(e)}")

if __name__ == "__main__":
    # Attente pour s'assurer que les services sont prêts
    print("Attente du démarrage des services (5 secondes)...")
    time.sleep(5)
    
    print("\nTest de l'endpoint reset-queue...")
    test_reset_queue_local() 