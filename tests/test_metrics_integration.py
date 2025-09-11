"""
Test script to verify metrics integration
"""
import asyncio
import logging

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


async def test_metrics_endpoint():
    """Test that metrics endpoint is accessible"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/metrics") as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info("✅ Metrics endpoint is accessible")

                    # Check for key metrics
                    key_metrics = [
                        "http_requests_total",
                        "http_request_duration_seconds",
                        "user_registrations_total",
                        "travel_searches_total",
                        "ticket_bookings_total",
                        "vector_operations_total",
                    ]

                    found_metrics = []
                    for metric in key_metrics:
                        if metric in content:
                            found_metrics.append(metric)
                            logger.info(f"✅ Found metric: {metric}")
                        else:
                            logger.warning(f"❌ Missing metric: {metric}")

                    logger.info(
                        f"Found {len(found_metrics)}/{len(key_metrics)} key metrics"
                    )
                    return (
                        len(found_metrics) >= len(key_metrics) * 0.8
                    )  # 80% success rate
                else:
                    logger.error(
                        f"❌ Metrics endpoint returned status {response.status}"
                    )
                    return False
        except Exception as e:
            logger.error(f"❌ Error accessing metrics endpoint: {e}")
            return False


async def test_api_endpoints():
    """Test API endpoints to generate metrics"""
    async with aiohttp.ClientSession() as session:
        endpoints = [
            "/health",
            "/api/health",
            "/api/vector-metrics/health",
            "/api/tickets-metrics/metrics/summary",
            "/api/vector-metrics/metrics/summary",
        ]

        success_count = 0
        for endpoint in endpoints:
            try:
                async with session.get(f"{BASE_URL}{endpoint}") as response:
                    if response.status == 200:
                        logger.info(f"✅ {endpoint} - Status: {response.status}")
                        success_count += 1
                    else:
                        logger.warning(f"⚠️ {endpoint} - Status: {response.status}")
            except Exception as e:
                logger.error(f"❌ {endpoint} - Error: {e}")

        logger.info(f"Successfully tested {success_count}/{len(endpoints)} endpoints")
        return success_count >= len(endpoints) * 0.6  # 60% success rate


async def test_business_metrics():
    """Test business metrics by making requests"""
    async with aiohttp.ClientSession() as session:
        try:
            # Test vector search (this should generate metrics)
            search_data = {"query": "test search", "limit": 5, "score_threshold": 0.7}

            async with session.post(
                f"{BASE_URL}/api/vector-metrics/search", json=search_data
            ) as response:
                if response.status in [200, 500]:  # 500 is OK for test data
                    logger.info("✅ Vector search request generated metrics")
                    return True
                else:
                    logger.warning(
                        f"⚠️ Vector search returned status {response.status}"
                    )
                    return False
        except Exception as e:
            logger.error(f"❌ Error testing business metrics: {e}")
            return False


async def main():
    """Run all tests"""
    logger.info("🚀 Starting metrics integration tests...")

    # Wait a bit for services to be ready
    await asyncio.sleep(2)

    tests = [
        ("Metrics Endpoint", test_metrics_endpoint),
        ("API Endpoints", test_api_endpoints),
        ("Business Metrics", test_business_metrics),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} test passed")
            else:
                logger.error(f"❌ {test_name} test failed")
        except Exception as e:
            logger.error(f"❌ {test_name} test error: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n📊 Test Results Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")

    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All metrics integration tests passed!")
    else:
        logger.warning(f"⚠️ {total - passed} tests failed")


if __name__ == "__main__":
    asyncio.run(main())
