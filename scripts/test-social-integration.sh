#!/usr/bin/env bash
# Run the social media integration test.
#
# This test posts to REAL social media accounts (Instagram, Facebook, LinkedIn),
# verifies the posts, then deletes them.
#
# Prerequisites:
#   1. Copy .env.social.example to .env.social and fill in credentials
#   2. Virtual environment activated
#
# Usage:
#   ./scripts/test-social-integration.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOCIAL_ENV="$REPO_ROOT/.env.social"

# Check .env.social exists
if [ ! -f "$SOCIAL_ENV" ]; then
    echo "❌ $SOCIAL_ENV not found."
    echo "   Copy .env.social.example to .env.social and fill in your credentials."
    exit 1
fi

# Show what will happen
echo ""
echo "========================================================================"
echo "⚠️  SOCIAL MEDIA INTEGRATION TEST"
echo "========================================================================"
echo ""
echo "This will:"
echo "  1. Create a test duck (ID 29999) in the test DB"
echo "  2. Post to all configured social platforms"
echo "  3. Verify posts exist"
echo "  4. Wait 10s for you to inspect"
echo "  5. Delete all social posts (DB rolls back automatically)"
echo ""
echo "Credentials from: $SOCIAL_ENV"
echo ""
echo "Configured platforms:"

# Show which platforms have creds (without revealing values)
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    if [ -n "$value" ]; then
        case "$key" in
            IG_USER_ID)       echo "  ✓ Instagram (IG_USER_ID set)" ;;
            FB_PAGE_ID)       echo "  ✓ Facebook (FB_PAGE_ID set)" ;;
            LI_ACCESS_TOKEN)  echo "  ✓ LinkedIn (LI_ACCESS_TOKEN set)" ;;
        esac
    fi
done < "$SOCIAL_ENV"

echo ""
read -p "Proceed? [y/N]: " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Running test..."
echo ""

cd "$REPO_ROOT/django"

# Load .env.social creds + set opt-in flag, then run the Django test
env RUN_SOCIAL_INTEGRATION_TESTS=yes $(cat "$SOCIAL_ENV" | grep -v '^#' | grep -v '^$' | xargs) \
    python manage.py test duck.tests.test_social_integration -v 2 --no-input
