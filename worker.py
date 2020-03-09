from globals import *
from netutils import send_message_to_colleague

def _is_prime(n):
    if n == 2 or n == 3: return True
    if n % 2 == 0 or n < 2: return False
    for i in range(3, int(n ** 0.5) + 1, 2):  # only odd numbers
        if n % i == 0:
            return False

    return True


class Worker:
    _found_primes = []

    def Worker(self):
        print("Worker created")

    def handle_colleague_death(self):
        pass

    def get_progress(self):
        print("Returning progress. Vector of ", len(self._found_primes), " primes")
        return self._found_primes

    def work(self, start):
        start = int(start)
        print("Finding primes in block starting:",start)
        half_block = int(WORK_BLOCK_SIZE/2)
        for num in range(start, start + half_block):
            if _is_prime(num):
                print("Found prime:", num)
                self._found_primes.append(num)
        print("Found ", len(self._found_primes), " in block")

        for num in range(start+half_block, start + WORK_BLOCK_SIZE):
            if _is_prime(num):
                print("Found prime:", num)
                self._found_primes.append(num)
        print("Found ", len(self._found_primes), " in block")
