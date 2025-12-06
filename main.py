import sys
from src.agent import Agent

def main():
    print("===========================================")
    print("🤖 Kişisel AI Asistanına Hoş Geldiniz")
    print("Çıkmak için 'q' veya 'exit' yazın.")
    print("===========================================")

    try:
        # Agent'ı yükle
        my_agent = Agent()
    except Exception as e:
        print(f" Hata: Agent başlatılamadı. .env dosyasını veya internet bağlantını kontrol et.\nDetay: {e}")
        return

    while True:
        try:
            user_input = input("\nSen: ")
            if user_input.lower() in ['q', 'exit', 'çık']:
                print("Güle güle! ")
                break
            
            if not user_input.strip():
                continue

            response = my_agent.chat(user_input)
            print(f"\nAsistan: {response}")

        except KeyboardInterrupt:
            print("\nProgram sonlandırıldı.")
            break
        except Exception as e:
            print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    main()