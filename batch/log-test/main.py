import time

if __name__ == "__main__":
    print("Python Scropt Started.")
    for i in range(20):
        print(f'Sleep {i**2} seconds.')
        time.sleep(i**2)
        

    print('Python Script Finished.')