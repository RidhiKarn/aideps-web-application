#!/usr/bin/env python3
"""
Performance testing for AIDEPS application
Tests response times, load handling, and resource usage
"""

import requests
import time
import statistics
import concurrent.futures
import pandas as pd
from io import BytesIO
from datetime import datetime

# Configuration
BACKEND_URL = "http://172.25.82.250:8000"
FRONTEND_URL = "http://172.25.82.250:3000"
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_failure(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

class PerformanceTester:
    def __init__(self):
        self.response_times = {}
        self.thresholds = {
            'excellent': 100,   # ms
            'good': 500,       # ms
            'acceptable': 1000, # ms
            'slow': 2000       # ms
        }
    
    def measure_response_time(self, url, method='GET', data=None, files=None):
        """Measure response time for a single request"""
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)
            else:
                return None, None
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            return response_time, response.status_code
        except Exception as e:
            return None, str(e)
    
    def evaluate_performance(self, response_time):
        """Evaluate performance based on response time"""
        if response_time is None:
            return "Failed", Colors.RED
        elif response_time < self.thresholds['excellent']:
            return "Excellent", Colors.GREEN
        elif response_time < self.thresholds['good']:
            return "Good", Colors.GREEN
        elif response_time < self.thresholds['acceptable']:
            return "Acceptable", Colors.YELLOW
        elif response_time < self.thresholds['slow']:
            return "Slow", Colors.YELLOW
        else:
            return "Very Slow", Colors.RED
    
    def test_endpoint_performance(self):
        """Test performance of individual endpoints"""
        print_header("Endpoint Performance Test")
        
        endpoints = [
            ("GET", f"{BACKEND_URL}/", "Root endpoint"),
            ("GET", f"{API_BASE}/documents", "List documents"),
            ("GET", f"{API_BASE}/workflows", "List workflows"),
            ("GET", f"{BACKEND_URL}/docs", "API documentation"),
            ("GET", f"{FRONTEND_URL}/", "Frontend homepage"),
        ]
        
        results = []
        
        for method, url, description in endpoints:
            response_time, status = self.measure_response_time(url, method)
            
            if response_time is not None:
                rating, color = self.evaluate_performance(response_time)
                print(f"{color}• {description}: {response_time:.2f}ms ({rating}){Colors.ENDC}")
                results.append(response_time)
            else:
                print_failure(f"• {description}: Failed - {status}")
        
        if results:
            print(f"\n{Colors.BOLD}Statistics:{Colors.ENDC}")
            print(f"  Average: {statistics.mean(results):.2f}ms")
            print(f"  Median: {statistics.median(results):.2f}ms")
            print(f"  Min: {min(results):.2f}ms")
            print(f"  Max: {max(results):.2f}ms")
    
    def test_file_upload_performance(self):
        """Test file upload performance with different sizes"""
        print_header("File Upload Performance Test")
        
        file_sizes = [
            (10, "Small (10 rows)"),
            (100, "Medium (100 rows)"),
            (1000, "Large (1000 rows)"),
            (5000, "Very Large (5000 rows)")
        ]
        
        for rows, description in file_sizes:
            # Create test data
            df = pd.DataFrame({
                'col1': range(rows),
                'col2': [f'value_{i}' for i in range(rows)],
                'col3': [i * 1.5 for i in range(rows)]
            })
            
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            files = {
                'file': (f'perf_test_{rows}.csv', csv_buffer, 'text/csv')
            }
            
            data = {
                'document_name': f'Performance Test {rows}',
                'organization': 'Test',
                'survey_type': 'test'
            }
            
            response_time, status = self.measure_response_time(
                f"{API_BASE}/documents/upload",
                method='POST',
                files=files,
                data=data
            )
            
            if response_time is not None:
                rating, color = self.evaluate_performance(response_time)
                print(f"{color}• {description}: {response_time:.2f}ms ({rating}){Colors.ENDC}")
                
                # Calculate throughput
                file_size_kb = csv_buffer.tell() / 1024
                if response_time > 0:
                    throughput = (file_size_kb / response_time) * 1000  # KB/s
                    print(f"  └─ Throughput: {throughput:.2f} KB/s")
            else:
                print_failure(f"• {description}: Failed - {status}")
    
    def test_concurrent_requests(self):
        """Test system performance under concurrent load"""
        print_header("Concurrent Request Performance Test")
        
        def make_request(url):
            return self.measure_response_time(url)
        
        concurrent_levels = [1, 5, 10, 20]
        url = f"{BACKEND_URL}/"
        
        for level in concurrent_levels:
            print_info(f"Testing with {level} concurrent requests")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=level) as executor:
                start_time = time.time()
                futures = [executor.submit(make_request, url) for _ in range(level)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
                total_time = (time.time() - start_time) * 1000
                
                successful = [r[0] for r in results if r[0] is not None]
                
                if successful:
                    avg_response = statistics.mean(successful)
                    rating, color = self.evaluate_performance(avg_response)
                    
                    print(f"{color}  Average response: {avg_response:.2f}ms ({rating}){Colors.ENDC}")
                    print(f"  Total time: {total_time:.2f}ms")
                    print(f"  Successful: {len(successful)}/{level}")
                    
                    if total_time > 0:
                        throughput = (level / total_time) * 1000  # requests/second
                        print(f"  Throughput: {throughput:.2f} req/s")
                else:
                    print_failure(f"  All requests failed")
    
    def test_stress_limits(self):
        """Test system stress limits"""
        print_header("Stress Test")
        
        print_info("Testing rapid sequential requests")
        
        url = f"{BACKEND_URL}/"
        num_requests = 50
        response_times = []
        
        start_time = time.time()
        
        for i in range(num_requests):
            response_time, status = self.measure_response_time(url)
            if response_time is not None:
                response_times.append(response_time)
            
            # Show progress every 10 requests
            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{num_requests} requests")
        
        total_time = (time.time() - start_time) * 1000
        
        if response_times:
            print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
            print(f"  Successful: {len(response_times)}/{num_requests}")
            print(f"  Average response: {statistics.mean(response_times):.2f}ms")
            print(f"  Median response: {statistics.median(response_times):.2f}ms")
            print(f"  95th percentile: {statistics.quantiles(response_times, n=20)[18]:.2f}ms")
            print(f"  Total time: {total_time:.2f}ms")
            print(f"  Throughput: {(num_requests / total_time) * 1000:.2f} req/s")
            
            # Check for performance degradation
            first_10_avg = statistics.mean(response_times[:10])
            last_10_avg = statistics.mean(response_times[-10:])
            degradation = ((last_10_avg - first_10_avg) / first_10_avg) * 100
            
            if degradation > 20:
                print_warning(f"  Performance degradation detected: {degradation:.1f}%")
            else:
                print_success(f"  Performance stable (degradation: {degradation:.1f}%)")
        else:
            print_failure("All requests failed")
    
    def test_memory_leak(self):
        """Test for potential memory leaks"""
        print_header("Memory Leak Test")
        
        print_info("Testing repeated operations for memory leaks")
        
        # Create small test file
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['A', 'B', 'C']
        })
        
        response_times = []
        
        for i in range(10):
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            files = {
                'file': (f'leak_test_{i}.csv', csv_buffer, 'text/csv')
            }
            
            data = {
                'document_name': f'Leak Test {i}',
                'organization': 'Test',
                'survey_type': 'test'
            }
            
            response_time, status = self.measure_response_time(
                f"{API_BASE}/documents/upload",
                method='POST',
                files=files,
                data=data
            )
            
            if response_time is not None:
                response_times.append(response_time)
            
            time.sleep(0.5)  # Brief pause between uploads
        
        if len(response_times) >= 2:
            # Check if response times are increasing (potential memory leak indicator)
            first_half_avg = statistics.mean(response_times[:5])
            second_half_avg = statistics.mean(response_times[5:])
            
            increase = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            
            if increase > 30:
                print_warning(f"Potential memory leak detected: {increase:.1f}% increase")
            else:
                print_success(f"No memory leak detected (change: {increase:.1f}%)")
    
    def test_caching_performance(self):
        """Test caching effectiveness"""
        print_header("Caching Performance Test")
        
        url = f"{BACKEND_URL}/"
        
        print_info("Testing cold cache")
        cold_time, _ = self.measure_response_time(url)
        
        print_info("Testing warm cache (5 repeated requests)")
        warm_times = []
        for _ in range(5):
            response_time, _ = self.measure_response_time(url)
            if response_time is not None:
                warm_times.append(response_time)
        
        if cold_time and warm_times:
            avg_warm = statistics.mean(warm_times)
            improvement = ((cold_time - avg_warm) / cold_time) * 100
            
            print(f"  Cold cache: {cold_time:.2f}ms")
            print(f"  Warm cache average: {avg_warm:.2f}ms")
            
            if improvement > 0:
                print_success(f"  Cache improvement: {improvement:.1f}%")
            else:
                print_info(f"  No cache improvement detected")

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}AIDEPS Performance Testing Suite{Colors.ENDC}")
    print(f"{Colors.BOLD}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    # Check if services are running
    try:
        requests.get(BACKEND_URL, timeout=2)
        print_success("Backend is accessible")
    except:
        print_failure("Backend not accessible - please start it first")
        return
    
    try:
        requests.get(FRONTEND_URL, timeout=2)
        print_success("Frontend is accessible")
    except:
        print_warning("Frontend not fully accessible")
    
    # Run performance tests
    tester = PerformanceTester()
    
    tester.test_endpoint_performance()
    tester.test_file_upload_performance()
    tester.test_concurrent_requests()
    tester.test_stress_limits()
    tester.test_memory_leak()
    tester.test_caching_performance()
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Performance Test Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    print_success("Performance testing completed")
    print_info("Review results above for performance bottlenecks")
    
    print(f"\n{Colors.BOLD}Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")

if __name__ == "__main__":
    main()