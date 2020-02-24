class Worker:
    _found_primes = []

    def Worker(self):
        print("Worker created")

    def get_progress(self):
        print("Returning progress. Vector of ", len(self._found_primes), " primes")
        return self._found_primes

    def _is_prime(self, n):
        if n == 2 or n == 3: return True
        if n % 2 == 0 or n < 2: return False
        for i in range(3, int(n ** 0.5) + 1, 2):  # only odd numbers
            if n % i == 0:
                return False

        return True

    def work(self):
        # work = get_work()
        todo = [1, 2, 3]
        for num in todo:
            if self._is_prime(num):
                print("Found prime:", num)
                self._found_primes.append(num)
